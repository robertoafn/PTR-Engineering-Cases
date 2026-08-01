using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Runtime.Serialization;
using System.Runtime.Serialization.Json;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;

namespace PtrEngineeringCases.DwsimAutomation
{
    [DataContract]
    internal sealed class RunnerResult
    {
        public RunnerResult()
        {
            SchemaVersion = "1.0.0";
            ExpectedDwsimVersion = "9.0.5";
            Errors = new List<ErrorResult>();
            Objects = new List<ObjectResult>();
            RequestedObjects = new List<string>();
            MissingObjects = new List<string>();
        }

        [DataMember(Name = "schema_version", Order = 1)]
        public string SchemaVersion { get; set; }

        [DataMember(Name = "timestamp_utc", Order = 2)]
        public string TimestampUtc { get; set; }

        [DataMember(Name = "dwsim_version", Order = 3)]
        public string DwsimVersion { get; set; }

        [DataMember(Name = "expected_dwsim_version", Order = 4)]
        public string ExpectedDwsimVersion { get; set; }

        [DataMember(Name = "version_compatible", Order = 5)]
        public bool VersionCompatible { get; set; }

        [DataMember(Name = "simulation_path", Order = 6)]
        public string SimulationPath { get; set; }

        [DataMember(Name = "simulation_sha256", Order = 7)]
        public string SimulationSha256 { get; set; }

        [DataMember(Name = "simulation_sha256_after", Order = 8)]
        public string SimulationSha256After { get; set; }

        [DataMember(Name = "source_unchanged", Order = 9)]
        public bool SourceUnchanged { get; set; }

        [DataMember(Name = "solved", Order = 10)]
        public bool Solved { get; set; }

        [DataMember(Name = "errors", Order = 11)]
        public List<ErrorResult> Errors { get; set; }

        [DataMember(Name = "objects", Order = 12)]
        public List<ObjectResult> Objects { get; set; }

        [DataMember(Name = "requested_objects", Order = 13)]
        public List<string> RequestedObjects { get; set; }

        [DataMember(Name = "missing_objects", Order = 14)]
        public List<string> MissingObjects { get; set; }
    }

    [DataContract]
    internal sealed class ErrorResult
    {
        [DataMember(Name = "type", Order = 1)]
        public string Type { get; set; }

        [DataMember(Name = "message", Order = 2)]
        public string Message { get; set; }

        [DataMember(Name = "stack_trace", Order = 3)]
        public string StackTrace { get; set; }
    }

    [DataContract]
    internal sealed class ObjectResult
    {
        public ObjectResult()
        {
            Warnings = new List<string>();
        }

        [DataMember(Name = "object_id", Order = 1)]
        public string ObjectId { get; set; }

        [DataMember(Name = "object_tag", Order = 2)]
        public string ObjectTag { get; set; }

        [DataMember(Name = "object_type", Order = 3)]
        public string ObjectType { get; set; }

        [DataMember(Name = "is_material_stream", Order = 4)]
        public bool IsMaterialStream { get; set; }

        [DataMember(Name = "temperature_K", Order = 5)]
        public double? TemperatureK { get; set; }

        [DataMember(Name = "pressure_Pa", Order = 6)]
        public double? PressurePa { get; set; }

        [DataMember(Name = "mass_flow_kg_s", Order = 7)]
        public double? MassFlowKgS { get; set; }

        [DataMember(Name = "specific_enthalpy_kJ_kg", Order = 8)]
        public double? SpecificEnthalpyKJkg { get; set; }

        [DataMember(Name = "energy_flow_kW", Order = 9)]
        public double? EnergyFlowKW { get; set; }

        [DataMember(Name = "duty_kW", Order = 10)]
        public double? DutyKW { get; set; }

        [DataMember(Name = "warnings", Order = 11)]
        public List<string> Warnings { get; set; }
    }

    internal sealed class CommandLineOptions
    {
        public CommandLineOptions()
        {
            ExpectedVersion = "9.0.5";
            ObjectIds = new List<string>();
        }

        public string SimulationPath { get; set; }
        public string DwsimHome { get; set; }
        public string ExpectedVersion { get; set; }
        public List<string> ObjectIds { get; private set; }
        public bool ShowHelp { get; set; }
    }

    internal static class Program
    {
        private static string _dwsimHome;

        private static readonly string[] TemperatureMembers =
        {
            "GetTemperature", "Temperature", "temperature"
        };

        private static readonly string[] PressureMembers =
        {
            "GetPressure", "Pressure", "pressure"
        };

        private static readonly string[] MassFlowMembers =
        {
            "GetMassFlow", "MassFlow", "massflow", "MassFlowRate"
        };

        private static readonly string[] EnthalpyMembers =
        {
            "GetMassEnthalpy", "GetSpecificEnthalpy", "SpecificEnthalpy",
            "MassEnthalpy", "Enthalpy", "enthalpy"
        };

        private static readonly string[] EnergyFlowMembers =
        {
            "GetEnergyFlow", "EnergyFlow", "energyflow", "Energy", "Power"
        };

        private static readonly string[] DutyMembers =
        {
            "GetHeatDuty", "GetDuty", "Duty", "HeatDuty", "HeatLoad",
            "DeltaQ", "Q", "Power", "EnergyFlow"
        };

        [STAThread]
        private static int Main(string[] args)
        {
            Console.OutputEncoding = new UTF8Encoding(false);

            CommandLineOptions options;
            string argumentError;
            if (!TryParseArguments(args, out options, out argumentError))
            {
                Console.Error.WriteLine(argumentError);
                PrintUsage(Console.Error);
                return 2;
            }

            if (options.ShowHelp)
            {
                PrintUsage(Console.Out);
                return 0;
            }

            return Run(options);
        }

        private static int Run(CommandLineOptions options)
        {
            RunnerResult result = new RunnerResult();
            result.TimestampUtc = DateTime.UtcNow.ToString("o", CultureInfo.InvariantCulture);
            result.ExpectedDwsimVersion = NormalizeExpectedVersion(options.ExpectedVersion);
            result.RequestedObjects.AddRange(options.ObjectIds);

            string initialDirectory = Directory.GetCurrentDirectory();
            string simulationPath = null;
            string temporaryDirectory = null;
            object automation = null;
            object flowsheet = null;
            TextWriter originalStandardOutput = Console.Out;
            StringWriter capturedDwsimOutput = new StringWriter(CultureInfo.InvariantCulture);
            bool standardOutputCaptured = false;
            bool solverCompleted = false;

            try
            {
                simulationPath = Path.GetFullPath(options.SimulationPath);
                result.SimulationPath = MakeRelativePath(initialDirectory, simulationPath);

                if (!File.Exists(simulationPath))
                {
                    AddError(result, "FileNotFoundException",
                        "No existe la simulación indicada: " + simulationPath, null);
                    return Finish(result, originalStandardOutput, capturedDwsimOutput, 1);
                }

                if (!String.Equals(Path.GetExtension(simulationPath), ".dwxmz",
                    StringComparison.OrdinalIgnoreCase))
                {
                    AddError(result, "InvalidSimulationExtension",
                        "El runner requiere una simulación DWSIM comprimida con extensión .dwxmz.", null);
                    return Finish(result, originalStandardOutput, capturedDwsimOutput, 1);
                }

                result.SimulationSha256 = ComputeSha256(simulationPath);
                _dwsimHome = ResolveDwsimHome(options.DwsimHome);
                if (_dwsimHome == null)
                {
                    AddError(result, "DwsimHomeNotFound",
                        "No se encontró DWSIM_HOME. Use --dwsim-home, la variable DWSIM_HOME o instale DWSIM en una ruta conocida.",
                        null);
                    return Finish(result, originalStandardOutput, capturedDwsimOutput, 1);
                }

                string automationAssemblyPath = Path.Combine(_dwsimHome, "DWSIM.Automation.dll");
                if (!File.Exists(automationAssemblyPath))
                {
                    AddError(result, "DwsimAssemblyNotFound",
                        "No existe DWSIM.Automation.dll en " + _dwsimHome, null);
                    return Finish(result, originalStandardOutput, capturedDwsimOutput, 1);
                }

                temporaryDirectory = Path.Combine(
                    Path.GetTempPath(),
                    "ptr-dwsim-" + Guid.NewGuid().ToString("N"));
                Directory.CreateDirectory(temporaryDirectory);
                string temporarySimulation = Path.Combine(
                    temporaryDirectory,
                    Path.GetFileName(simulationPath));
                File.Copy(simulationPath, temporarySimulation, false);

                string temporaryHash = ComputeSha256(temporarySimulation);
                if (!String.Equals(result.SimulationSha256, temporaryHash,
                    StringComparison.OrdinalIgnoreCase))
                {
                    AddError(result, "TemporaryCopyChecksumMismatch",
                        "La copia temporal no coincide byte a byte con la simulación de origen.", null);
                    return Finish(result, originalStandardOutput, capturedDwsimOutput, 1);
                }

                AppDomain.CurrentDomain.AssemblyResolve += ResolveDwsimAssembly;

                // Automation3 puede escribir mensajes propios en Console.Out. Se capturan para
                // mantener stdout como un único documento JSON estable.
                Console.SetOut(capturedDwsimOutput);
                standardOutputCaptured = true;
                Directory.SetCurrentDirectory(_dwsimHome);

                Assembly automationAssembly = Assembly.LoadFrom(automationAssemblyPath);
                Type automationType = automationAssembly.GetType(
                    "DWSIM.Automation.Automation3", true, false);
                automation = Activator.CreateInstance(automationType);

                result.DwsimVersion = Convert.ToString(
                    InvokeMethod(automation, "GetVersion", new object[0]),
                    CultureInfo.InvariantCulture);
                result.VersionCompatible = IsCompatibleVersion(
                    result.DwsimVersion,
                    result.ExpectedDwsimVersion);

                if (!result.VersionCompatible)
                {
                    AddError(result, "DwsimVersionMismatch",
                        "Se esperaba DWSIM " + result.ExpectedDwsimVersion
                        + " y GetVersion() informó: " + result.DwsimVersion,
                        null);
                }
                else
                {
                    flowsheet = InvokeMethod(
                        automation,
                        "LoadFlowsheet",
                        new object[] { temporarySimulation });

                    object solverResult = InvokeMethod(
                        automation,
                        "CalculateFlowsheet4",
                        new object[] { flowsheet });

                    int solverErrorCount = AppendSolverErrors(result, solverResult);
                    solverCompleted = solverErrorCount == 0;
                    result.Solved = solverCompleted;

                    ExtractObjects(flowsheet, options.ObjectIds, result);
                }
            }
            catch (TargetInvocationException exception)
            {
                Exception cause = exception.InnerException ?? exception;
                AddException(result, "DwsimInvocationError", cause);
                result.Solved = false;
            }
            catch (Exception exception)
            {
                AddException(result, "RunnerError", exception);
                result.Solved = false;
            }
            finally
            {
                try
                {
                    ReleaseFlowsheet(flowsheet);
                }
                catch (Exception exception)
                {
                    AddException(result, "FlowsheetReleaseWarning", Unwrap(exception));
                }

                try
                {
                    if (automation != null)
                    {
                        InvokeMethod(automation, "ReleaseResources", new object[0]);
                        if (Marshal.IsComObject(automation))
                        {
                            Marshal.FinalReleaseComObject(automation);
                        }
                    }
                }
                catch (Exception exception)
                {
                    AddException(result, "AutomationReleaseWarning", Unwrap(exception));
                }

                AppDomain.CurrentDomain.AssemblyResolve -= ResolveDwsimAssembly;

                try
                {
                    Directory.SetCurrentDirectory(initialDirectory);
                }
                catch (Exception exception)
                {
                    AddException(result, "WorkingDirectoryRestoreWarning", exception);
                }

                if (standardOutputCaptured)
                {
                    Console.SetOut(originalStandardOutput);
                }

                ForwardCapturedDwsimOutput(capturedDwsimOutput);

                if (temporaryDirectory != null)
                {
                    try
                    {
                        string absoluteTemporaryDirectory = Path.GetFullPath(temporaryDirectory);
                        string absoluteSystemTemp = EnsureTrailingSeparator(
                            Path.GetFullPath(Path.GetTempPath()));
                        if (absoluteTemporaryDirectory.StartsWith(
                            absoluteSystemTemp,
                            StringComparison.OrdinalIgnoreCase)
                            && Path.GetFileName(absoluteTemporaryDirectory).StartsWith(
                                "ptr-dwsim-",
                                StringComparison.OrdinalIgnoreCase))
                        {
                            Directory.Delete(absoluteTemporaryDirectory, true);
                        }
                    }
                    catch (Exception exception)
                    {
                        AddException(result, "TemporaryCleanupWarning", exception);
                    }
                }

                if (simulationPath != null && File.Exists(simulationPath))
                {
                    try
                    {
                        result.SimulationSha256After = ComputeSha256(simulationPath);
                        result.SourceUnchanged = String.Equals(
                            result.SimulationSha256,
                            result.SimulationSha256After,
                            StringComparison.OrdinalIgnoreCase);
                        if (!result.SourceUnchanged)
                        {
                            AddError(result, "SourceSimulationChanged",
                                "El checksum de la simulación de origen cambió durante la ejecución.",
                                null);
                        }
                    }
                    catch (Exception exception)
                    {
                        AddException(result, "SourceChecksumAfterError", exception);
                    }
                }
            }

            bool missingRequestedObjects = result.MissingObjects.Count > 0;
            bool successful = result.VersionCompatible
                              && solverCompleted
                              && result.SourceUnchanged
                              && !missingRequestedObjects
                              && !ContainsFatalRuntimeError(result.Errors);
            return Finish(result, originalStandardOutput, capturedDwsimOutput, successful ? 0 : 1);
        }

        private static int Finish(
            RunnerResult result,
            TextWriter originalStandardOutput,
            StringWriter capturedDwsimOutput,
            int exitCode)
        {
            if (!Object.ReferenceEquals(Console.Out, originalStandardOutput))
            {
                Console.SetOut(originalStandardOutput);
            }

            ForwardCapturedDwsimOutput(capturedDwsimOutput);
            Console.Out.WriteLine(SerializeJson(result));
            Console.Out.Flush();
            return exitCode;
        }

        private static void ExtractObjects(
            object flowsheet,
            IList<string> requestedIds,
            RunnerResult result)
        {
            IList<KeyValuePair<string, object>> allObjects = EnumerateSimulationObjects(flowsheet);
            HashSet<string> unmatched = new HashSet<string>(
                requestedIds,
                StringComparer.OrdinalIgnoreCase);

            foreach (KeyValuePair<string, object> entry in allObjects)
            {
                object simulationObject = entry.Value;
                if (simulationObject == null)
                {
                    continue;
                }

                string name = ConvertToString(GetMemberValue(simulationObject, "Name"));
                object graphicObject = GetMemberValue(simulationObject, "GraphicObject");
                string tag = ConvertToString(GetMemberValue(graphicObject, "Tag"));
                if (tag != null)
                {
                    tag = tag.Trim();
                }
                string objectId = FirstNonEmpty(entry.Key, name, tag);

                bool selected = requestedIds.Count == 0;
                if (!selected)
                {
                    foreach (string requestedId in requestedIds)
                    {
                        if (MatchesIdentifier(requestedId, objectId, name, tag))
                        {
                            selected = true;
                            unmatched.Remove(requestedId);
                        }
                    }
                }

                if (!selected)
                {
                    continue;
                }

                ObjectResult objectResult = ExtractObject(
                    objectId,
                    tag,
                    simulationObject,
                    graphicObject);
                result.Objects.Add(objectResult);
            }

            foreach (string missingId in requestedIds)
            {
                if (unmatched.Contains(missingId))
                {
                    result.MissingObjects.Add(missingId);
                }
            }

            if (allObjects.Count == 0)
            {
                AddError(result, "ObjectExtractionError",
                    "El flowsheet no expuso objetos mediante SimulationObjects.", null);
            }
            else if (result.MissingObjects.Count > 0)
            {
                AddError(result, "RequestedObjectNotFound",
                    "No se encontraron los objetos solicitados: "
                    + String.Join(", ", result.MissingObjects.ToArray()), null);
            }
        }

        private static ObjectResult ExtractObject(
            string objectId,
            string tag,
            object simulationObject,
            object graphicObject)
        {
            ObjectResult result = new ObjectResult();
            result.ObjectId = objectId;
            result.ObjectTag = tag;

            string runtimeType = simulationObject.GetType().FullName;
            string graphicType = ConvertToString(GetMemberValue(graphicObject, "ObjectType"));
            result.ObjectType = FirstNonEmpty(graphicType, runtimeType, "Unknown");
            result.IsMaterialStream =
                ContainsIgnoreCase(runtimeType, "MaterialStream")
                || ContainsIgnoreCase(graphicType, "MaterialStream");

            result.TemperatureK = ReadNumericValue(
                simulationObject, TemperatureMembers, true);
            result.PressurePa = ReadNumericValue(
                simulationObject, PressureMembers, true);
            result.MassFlowKgS = ReadNumericValue(
                simulationObject, MassFlowMembers, true);
            result.SpecificEnthalpyKJkg = ReadNumericValue(
                simulationObject, EnthalpyMembers, true);
            result.EnergyFlowKW = ReadNumericValue(
                simulationObject, EnergyFlowMembers, false);
            result.DutyKW = ReadNumericValue(
                simulationObject, DutyMembers, false);

            if (result.IsMaterialStream)
            {
                if (result.MassFlowKgS.HasValue
                    && result.SpecificEnthalpyKJkg.HasValue)
                {
                    // kg/s * kJ/kg = kJ/s = kW. No se altera el estado ni se
                    // aplica una convención de signo adicional. Se usa esta
                    // definición incluso si el objeto expone un miembro genérico
                    // llamado Energy, porque este puede representar energía
                    // acumulada y no flujo entálpico.
                    result.EnergyFlowKW =
                        result.MassFlowKgS.Value * result.SpecificEnthalpyKJkg.Value;
                }

                if (!result.TemperatureK.HasValue)
                {
                    result.Warnings.Add("temperature_K no disponible mediante la API genérica.");
                }
                if (!result.PressurePa.HasValue)
                {
                    result.Warnings.Add("pressure_Pa no disponible mediante la API genérica.");
                }
                if (!result.MassFlowKgS.HasValue)
                {
                    result.Warnings.Add("mass_flow_kg_s no disponible mediante la API genérica.");
                }
                if (!result.SpecificEnthalpyKJkg.HasValue)
                {
                    result.Warnings.Add("specific_enthalpy_kJ_kg no disponible mediante la API genérica.");
                }
            }

            return result;
        }

        private static double? ReadNumericValue(
            object simulationObject,
            string[] candidates,
            bool inspectOverallPhase)
        {
            double? value = ReadNumericMemberOrMethod(simulationObject, candidates);
            if (value.HasValue || !inspectOverallPhase)
            {
                return value;
            }

            object phases = GetMemberValue(simulationObject, "Phases");
            object overallPhase = GetDictionaryValue(phases, "0");
            if (overallPhase == null)
            {
                overallPhase = GetFirstDictionaryValue(phases);
            }

            if (overallPhase == null)
            {
                return null;
            }

            object phaseProperties = GetMemberValue(overallPhase, "Properties");
            value = ReadNumericMemberOrMethod(phaseProperties, candidates);
            if (value.HasValue)
            {
                return value;
            }

            return ReadNumericMemberOrMethod(overallPhase, candidates);
        }

        private static double? ReadNumericMemberOrMethod(object target, string[] candidates)
        {
            if (target == null)
            {
                return null;
            }

            Type targetType = target.GetType();
            foreach (string candidate in candidates)
            {
                try
                {
                    MethodInfo method = FindMethod(targetType, candidate, 0);
                    if (method != null)
                    {
                        double? convertedMethodValue = ConvertToFiniteDouble(
                            method.Invoke(target, new object[0]));
                        if (convertedMethodValue.HasValue)
                        {
                            return convertedMethodValue;
                        }
                    }
                }
                catch
                {
                    // Algunas operaciones unitarias exponen getters que no aplican a su
                    // modo de cálculo. Se continúa con el siguiente miembro candidato.
                }

                try
                {
                    PropertyInfo property = FindProperty(targetType, candidate);
                    if (property != null && property.GetIndexParameters().Length == 0)
                    {
                        double? convertedPropertyValue = ConvertToFiniteDouble(
                            property.GetValue(target, null));
                        if (convertedPropertyValue.HasValue)
                        {
                            return convertedPropertyValue;
                        }
                    }
                }
                catch
                {
                    // Véase el comentario anterior: un getter no aplicable no invalida
                    // la extracción de las demás propiedades.
                }
            }

            return null;
        }

        private static IList<KeyValuePair<string, object>> EnumerateSimulationObjects(
            object flowsheet)
        {
            List<KeyValuePair<string, object>> objects =
                new List<KeyValuePair<string, object>>();
            if (flowsheet == null)
            {
                return objects;
            }

            object collection = GetMemberValue(flowsheet, "SimulationObjects");
            if (collection == null)
            {
                try
                {
                    collection = InvokeMethod(
                        flowsheet,
                        "GetSimulationObjects",
                        new object[0]);
                }
                catch
                {
                    return objects;
                }
            }

            IEnumerable enumerable = collection as IEnumerable;
            if (enumerable == null)
            {
                return objects;
            }

            foreach (object item in enumerable)
            {
                if (item == null)
                {
                    continue;
                }

                object value = GetMemberValue(item, "Value");
                object key = GetMemberValue(item, "Key");
                if (value != null)
                {
                    objects.Add(new KeyValuePair<string, object>(
                        ConvertToString(key),
                        value));
                }
                else
                {
                    objects.Add(new KeyValuePair<string, object>(
                        ConvertToString(GetMemberValue(item, "Name")),
                        item));
                }
            }

            return objects;
        }

        private static object GetDictionaryValue(object dictionary, string expectedKey)
        {
            IEnumerable enumerable = dictionary as IEnumerable;
            if (enumerable == null)
            {
                return null;
            }

            foreach (object entry in enumerable)
            {
                object key = GetMemberValue(entry, "Key");
                if (String.Equals(
                    ConvertToString(key),
                    expectedKey,
                    StringComparison.OrdinalIgnoreCase))
                {
                    return GetMemberValue(entry, "Value");
                }
            }
            return null;
        }

        private static object GetFirstDictionaryValue(object dictionary)
        {
            IEnumerable enumerable = dictionary as IEnumerable;
            if (enumerable == null)
            {
                return null;
            }

            foreach (object entry in enumerable)
            {
                object value = GetMemberValue(entry, "Value");
                return value ?? entry;
            }
            return null;
        }

        private static int AppendSolverErrors(RunnerResult result, object solverResult)
        {
            if (solverResult == null)
            {
                return 0;
            }

            int count = 0;
            IEnumerable errors = solverResult as IEnumerable;
            if (errors == null)
            {
                return 0;
            }

            foreach (object item in errors)
            {
                Exception exception = item as Exception;
                if (exception != null)
                {
                    AddException(result, "DwsimSolverError", exception);
                }
                else if (item != null)
                {
                    AddError(result, "DwsimSolverError",
                        Convert.ToString(item, CultureInfo.InvariantCulture), null);
                }
                count++;
            }
            return count;
        }

        private static void ReleaseFlowsheet(object flowsheet)
        {
            if (flowsheet == null)
            {
                return;
            }

            IDisposable disposable = flowsheet as IDisposable;
            if (disposable != null)
            {
                disposable.Dispose();
                return;
            }

            MethodInfo disposeMethod = FindMethod(flowsheet.GetType(), "Dispose", 0);
            if (disposeMethod != null)
            {
                disposeMethod.Invoke(flowsheet, new object[0]);
            }
        }

        private static object InvokeMethod(object target, string name, object[] arguments)
        {
            if (target == null)
            {
                throw new ArgumentNullException("target");
            }

            MethodInfo method = FindCompatibleMethod(target.GetType(), name, arguments);
            if (method == null)
            {
                throw new MissingMethodException(target.GetType().FullName, name);
            }
            return method.Invoke(target, arguments);
        }

        private static MethodInfo FindCompatibleMethod(
            Type targetType,
            string name,
            object[] arguments)
        {
            MethodInfo[] methods = targetType.GetMethods(BindingFlags.Public | BindingFlags.Instance);
            foreach (MethodInfo method in methods)
            {
                if (!String.Equals(method.Name, name, StringComparison.OrdinalIgnoreCase))
                {
                    continue;
                }

                ParameterInfo[] parameters = method.GetParameters();
                if (parameters.Length != arguments.Length)
                {
                    continue;
                }

                bool compatible = true;
                for (int index = 0; index < parameters.Length; index++)
                {
                    if (arguments[index] != null
                        && !parameters[index].ParameterType.IsInstanceOfType(arguments[index])
                        && parameters[index].ParameterType != typeof(string))
                    {
                        compatible = false;
                        break;
                    }
                }

                if (compatible)
                {
                    return method;
                }
            }
            return null;
        }

        private static MethodInfo FindMethod(Type targetType, string name, int argumentCount)
        {
            MethodInfo[] methods = targetType.GetMethods(BindingFlags.Public | BindingFlags.Instance);
            foreach (MethodInfo method in methods)
            {
                if (String.Equals(method.Name, name, StringComparison.OrdinalIgnoreCase)
                    && method.GetParameters().Length == argumentCount)
                {
                    return method;
                }
            }
            return null;
        }

        private static PropertyInfo FindProperty(Type targetType, string name)
        {
            PropertyInfo[] properties = targetType.GetProperties(
                BindingFlags.Public | BindingFlags.Instance);
            foreach (PropertyInfo property in properties)
            {
                if (String.Equals(property.Name, name, StringComparison.OrdinalIgnoreCase))
                {
                    return property;
                }
            }
            return null;
        }

        private static object GetMemberValue(object target, string name)
        {
            if (target == null)
            {
                return null;
            }

            try
            {
                PropertyInfo property = FindProperty(target.GetType(), name);
                if (property != null && property.GetIndexParameters().Length == 0)
                {
                    return property.GetValue(target, null);
                }

                FieldInfo field = target.GetType().GetField(
                    name,
                    BindingFlags.Public
                    | BindingFlags.Instance
                    | BindingFlags.IgnoreCase);
                if (field != null)
                {
                    return field.GetValue(target);
                }
            }
            catch
            {
                return null;
            }
            return null;
        }

        private static double? ConvertToFiniteDouble(object value)
        {
            if (value == null)
            {
                return null;
            }

            try
            {
                double converted = Convert.ToDouble(value, CultureInfo.InvariantCulture);
                if (Double.IsNaN(converted) || Double.IsInfinity(converted))
                {
                    return null;
                }
                return converted;
            }
            catch
            {
                return null;
            }
        }

        private static Assembly ResolveDwsimAssembly(object sender, ResolveEventArgs args)
        {
            if (String.IsNullOrWhiteSpace(_dwsimHome))
            {
                return null;
            }

            try
            {
                string simpleName = new AssemblyName(args.Name).Name;
                string[] directories =
                {
                    _dwsimHome,
                    Path.Combine(_dwsimHome, "extenders"),
                    Path.Combine(_dwsimHome, "ppacks")
                };
                string[] extensions = { ".dll", ".exe" };

                foreach (string directory in directories)
                {
                    foreach (string extension in extensions)
                    {
                        string candidate = Path.Combine(directory, simpleName + extension);
                        if (File.Exists(candidate))
                        {
                            return Assembly.LoadFrom(candidate);
                        }
                    }
                }
            }
            catch (Exception exception)
            {
                Console.Error.WriteLine(
                    "[runner] No se pudo resolver una dependencia DWSIM: "
                    + exception.Message);
            }
            return null;
        }

        private static string ResolveDwsimHome(string commandLineValue)
        {
            List<string> candidates = new List<string>();
            AddCandidate(candidates, commandLineValue);
            AddCandidate(candidates, Environment.GetEnvironmentVariable("DWSIM_HOME"));
            AddCandidate(candidates, Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                "DWSIM"));
            AddCandidate(candidates, Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles),
                "DWSIM"));

            foreach (string candidate in candidates)
            {
                try
                {
                    string fullPath = Path.GetFullPath(
                        Environment.ExpandEnvironmentVariables(candidate));
                    if (Directory.Exists(fullPath)
                        && File.Exists(Path.Combine(fullPath, "DWSIM.Automation.dll")))
                    {
                        return fullPath;
                    }
                }
                catch
                {
                    // Se prueba el siguiente candidato.
                }
            }
            return null;
        }

        private static void AddCandidate(ICollection<string> candidates, string value)
        {
            if (!String.IsNullOrWhiteSpace(value))
            {
                candidates.Add(value.Trim().Trim('"'));
            }
        }

        private static bool IsCompatibleVersion(string reportedVersion, string expectedVersion)
        {
            if (String.IsNullOrWhiteSpace(reportedVersion)
                || String.IsNullOrWhiteSpace(expectedVersion))
            {
                return false;
            }

            Match match = Regex.Match(
                reportedVersion,
                @"(?<!\d)(\d+\.\d+\.\d+)(?:\.\d+)?",
                RegexOptions.CultureInvariant);
            return match.Success
                   && String.Equals(
                       match.Groups[1].Value,
                       expectedVersion,
                       StringComparison.OrdinalIgnoreCase);
        }

        private static string NormalizeExpectedVersion(string version)
        {
            if (String.IsNullOrWhiteSpace(version))
            {
                return "9.0.5";
            }

            string normalized = version.Trim();
            if (normalized.StartsWith("v", StringComparison.OrdinalIgnoreCase))
            {
                normalized = normalized.Substring(1);
            }
            return normalized;
        }

        private static string ComputeSha256(string path)
        {
            using (SHA256 algorithm = SHA256.Create())
            using (FileStream stream = File.OpenRead(path))
            {
                byte[] digest = algorithm.ComputeHash(stream);
                StringBuilder builder = new StringBuilder(digest.Length * 2);
                foreach (byte value in digest)
                {
                    builder.Append(value.ToString("x2", CultureInfo.InvariantCulture));
                }
                return builder.ToString();
            }
        }

        private static string SerializeJson(RunnerResult result)
        {
            DataContractJsonSerializer serializer = new DataContractJsonSerializer(
                typeof(RunnerResult));
            using (MemoryStream stream = new MemoryStream())
            {
                serializer.WriteObject(stream, result);
                return Encoding.UTF8.GetString(stream.ToArray());
            }
        }

        private static void ForwardCapturedDwsimOutput(StringWriter capturedOutput)
        {
            if (capturedOutput == null)
            {
                return;
            }

            string text = capturedOutput.ToString();
            if (String.IsNullOrWhiteSpace(text))
            {
                return;
            }

            string[] lines = text.Replace("\r\n", "\n").Replace('\r', '\n').Split('\n');
            foreach (string line in lines)
            {
                if (!String.IsNullOrWhiteSpace(line))
                {
                    Console.Error.WriteLine("[DWSIM] " + line);
                }
            }
            capturedOutput.GetStringBuilder().Length = 0;
        }

        private static void AddException(
            RunnerResult result,
            string category,
            Exception exception)
        {
            AddError(
                result,
                category + ":" + exception.GetType().FullName,
                exception.Message,
                exception.StackTrace);
        }

        private static void AddError(
            RunnerResult result,
            string type,
            string message,
            string stackTrace)
        {
            result.Errors.Add(new ErrorResult
            {
                Type = type,
                Message = message,
                StackTrace = stackTrace
            });
        }

        private static Exception Unwrap(Exception exception)
        {
            TargetInvocationException invocationException =
                exception as TargetInvocationException;
            return invocationException != null && invocationException.InnerException != null
                ? invocationException.InnerException
                : exception;
        }

        private static bool ContainsFatalRuntimeError(IList<ErrorResult> errors)
        {
            foreach (ErrorResult error in errors)
            {
                if (error.Type.StartsWith("FlowsheetReleaseWarning", StringComparison.Ordinal)
                    || error.Type.StartsWith("AutomationReleaseWarning", StringComparison.Ordinal)
                    || error.Type.StartsWith("WorkingDirectoryRestoreWarning", StringComparison.Ordinal)
                    || error.Type.StartsWith("TemporaryCleanupWarning", StringComparison.Ordinal))
                {
                    continue;
                }
                return true;
            }
            return false;
        }

        private static bool MatchesIdentifier(
            string expected,
            string objectId,
            string name,
            string tag)
        {
            return String.Equals(expected, objectId, StringComparison.OrdinalIgnoreCase)
                   || String.Equals(expected, name, StringComparison.OrdinalIgnoreCase)
                   || String.Equals(expected, tag, StringComparison.OrdinalIgnoreCase);
        }

        private static string FirstNonEmpty(params string[] values)
        {
            foreach (string value in values)
            {
                if (!String.IsNullOrWhiteSpace(value))
                {
                    return value;
                }
            }
            return null;
        }

        private static string ConvertToString(object value)
        {
            return value == null
                ? null
                : Convert.ToString(value, CultureInfo.InvariantCulture);
        }

        private static bool ContainsIgnoreCase(string value, string fragment)
        {
            return value != null
                   && value.IndexOf(fragment, StringComparison.OrdinalIgnoreCase) >= 0;
        }

        private static string MakeRelativePath(string baseDirectory, string filePath)
        {
            try
            {
                Uri baseUri = new Uri(EnsureTrailingSeparator(Path.GetFullPath(baseDirectory)));
                Uri fileUri = new Uri(Path.GetFullPath(filePath));
                if (baseUri.Scheme == fileUri.Scheme)
                {
                    return Uri.UnescapeDataString(
                        baseUri.MakeRelativeUri(fileUri).ToString())
                        .Replace('/', Path.DirectorySeparatorChar);
                }
            }
            catch
            {
                // Se conserva la ruta absoluta si no puede relativizarse.
            }
            return Path.GetFullPath(filePath);
        }

        private static string EnsureTrailingSeparator(string path)
        {
            if (path.EndsWith(Path.DirectorySeparatorChar.ToString(), StringComparison.Ordinal)
                || path.EndsWith(Path.AltDirectorySeparatorChar.ToString(), StringComparison.Ordinal))
            {
                return path;
            }
            return path + Path.DirectorySeparatorChar;
        }

        private static bool TryParseArguments(
            string[] args,
            out CommandLineOptions options,
            out string error)
        {
            options = new CommandLineOptions();
            error = null;

            for (int index = 0; index < args.Length; index++)
            {
                string argument = args[index];
                if (argument == "--help" || argument == "-h" || argument == "/?")
                {
                    options.ShowHelp = true;
                    continue;
                }

                if (argument == "--simulation")
                {
                    if (!TryReadValue(args, ref index, out error))
                    {
                        return false;
                    }
                    options.SimulationPath = args[index];
                }
                else if (argument == "--dwsim-home")
                {
                    if (!TryReadValue(args, ref index, out error))
                    {
                        return false;
                    }
                    options.DwsimHome = args[index];
                }
                else if (argument == "--objects")
                {
                    if (!TryReadValue(args, ref index, out error))
                    {
                        return false;
                    }
                    AddObjectIds(options.ObjectIds, args[index]);
                }
                else if (argument == "--required-version")
                {
                    if (!TryReadValue(args, ref index, out error))
                    {
                        return false;
                    }
                    options.ExpectedVersion = args[index];
                }
                else
                {
                    error = "Argumento no reconocido: " + argument;
                    return false;
                }
            }

            if (!options.ShowHelp && String.IsNullOrWhiteSpace(options.SimulationPath))
            {
                error = "Falta el argumento obligatorio --simulation.";
                return false;
            }

            return true;
        }

        private static bool TryReadValue(
            string[] args,
            ref int index,
            out string error)
        {
            if (index + 1 >= args.Length
                || args[index + 1].StartsWith("--", StringComparison.Ordinal))
            {
                error = "Falta el valor para " + args[index] + ".";
                return false;
            }
            index++;
            error = null;
            return true;
        }

        private static void AddObjectIds(ICollection<string> target, string csv)
        {
            string[] values = csv.Split(',');
            foreach (string value in values)
            {
                string normalized = value.Trim();
                if (!String.IsNullOrWhiteSpace(normalized)
                    && !ContainsValueIgnoreCase(target, normalized))
                {
                    target.Add(normalized);
                }
            }
        }

        private static bool ContainsValueIgnoreCase(IEnumerable<string> values, string expected)
        {
            foreach (string value in values)
            {
                if (String.Equals(value, expected, StringComparison.OrdinalIgnoreCase))
                {
                    return true;
                }
            }
            return false;
        }

        private static void PrintUsage(TextWriter writer)
        {
            writer.WriteLine("PTR DWSIM Validation Runner");
            writer.WriteLine();
            writer.WriteLine("Uso:");
            writer.WriteLine(
                "  DwsimValidationRunner.exe --simulation <caso.dwxmz> "
                + "[--dwsim-home <ruta>] [--objects ID1,ID2] "
                + "[--required-version 9.0.5]");
            writer.WriteLine();
            writer.WriteLine("La salida normal en stdout es un único documento JSON.");
            writer.WriteLine("Los mensajes de DWSIM y del runner se escriben únicamente en stderr.");
        }
    }
}
