# Runner de validación DWSIM

Adaptador local y opcional para ejecutar simulaciones PTR con
`DWSIM.Automation.Automation3`. El ejecutable trabaja en un proceso independiente,
no guarda el flowsheet y entrega un único documento JSON por `stdout`.

El runner está orientado a DWSIM **9.0.5 para Windows x64**. No se usa en el
workflow ordinario de GitHub Actions: el validador Python debe recurrir a los
datasets exportados cuando DWSIM no esté disponible.

## Requisitos

- Windows x64.
- DWSIM 9.0.5 instalado.
- .NET Framework 4.6.2 o posterior.
- Compilador:
  `C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe`.

`DWSIM_HOME` se resuelve en este orden:

1. `--dwsim-home` o `-DwsimHome`, según se ejecute el runner o el script de
   compilación;
2. variable de entorno `DWSIM_HOME`;
3. `%LOCALAPPDATA%\DWSIM`;
4. `%ProgramFiles%\DWSIM`.

## Compilación reproducible

Desde la raíz del repositorio:

```powershell
.\tools\dwsim_automation_runner\build.ps1
```

Para seleccionar explícitamente la instalación y el destino:

```powershell
.\tools\dwsim_automation_runner\build.ps1 `
  -DwsimHome 'C:\Users\usuario\AppData\Local\DWSIM' `
  -OutputPath '.\tools\dwsim_automation_runner\bin\DwsimValidationRunner.exe'
```

El script invoca `csc.exe` con `/platform:x64` y referencias a
`DWSIM.Automation.dll` y `DWSIM.Interfaces.dll` obtenidas de `DWSIM_HOME`. Los
binarios y símbolos bajo `bin/` y `obj/` están excluidos de Git.

## Uso

```powershell
.\tools\dwsim_automation_runner\bin\DwsimValidationRunner.exe `
  --simulation '.\cases\001_ejemplo\simulations\caso.dwxmz'
```

Opciones:

```text
--simulation <ruta>          Archivo .dwxmz obligatorio.
--dwsim-home <ruta>          Instalación DWSIM que se utilizará.
--objects <ID1,ID2>          Limita la extracción a IDs, nombres o tags.
--required-version <X.Y.Z>   Versión exacta esperada; por defecto 9.0.5.
--help                       Muestra la ayuda.
```

La simulación original se lee para calcular SHA-256, se copia a un directorio
temporal y solo la copia se carga y resuelve. El runner:

1. compara `GetVersion()` con la versión requerida;
2. ejecuta `LoadFlowsheet()` sobre la copia;
3. llama a `CalculateFlowsheet4()`;
4. extrae los objetos;
5. llama a `ReleaseResources()` y elimina el temporal;
6. vuelve a calcular SHA-256 sobre el archivo original.

No se llama a `SaveFlowsheet`.

## Contrato JSON

Durante una ejecución normal, `stdout` contiene exclusivamente un documento
JSON. Los mensajes producidos por DWSIM se capturan y reenvían a `stderr`.

```json
{
  "schema_version": "1.0.0",
  "timestamp_utc": "2026-07-25T12:00:00.0000000Z",
  "dwsim_version": "DWSIM version 9.0.5.0 (...)",
  "expected_dwsim_version": "9.0.5",
  "version_compatible": true,
  "simulation_path": "cases\\001_ejemplo\\simulations\\caso.dwxmz",
  "simulation_sha256": "...",
  "simulation_sha256_after": "...",
  "source_unchanged": true,
  "solved": true,
  "errors": [],
  "objects": [
    {
      "object_id": "MSTR-001",
      "object_tag": "MSTR-001",
      "object_type": "MaterialStream",
      "is_material_stream": true,
      "temperature_K": 298.15,
      "pressure_Pa": 101325.0,
      "mass_flow_kg_s": 1.0,
      "specific_enthalpy_kJ_kg": 104.8,
      "energy_flow_kW": 104.8,
      "duty_kW": null,
      "warnings": []
    }
  ],
  "requested_objects": [],
  "missing_objects": []
}
```

Las unidades son las unidades SI internas usadas por la API DWSIM:

- temperatura: K;
- presión: Pa;
- flujo másico: kg/s;
- entalpía específica: kJ/kg;
- energía, potencia o deber térmico: kW.

Cuando una corriente material no expone `energy_flow_kW`, el runner lo calcula
como `mass_flow_kg_s * specific_enthalpy_kJ_kg`. Para equipos, `energy_flow_kW`
y `duty_kW` conservan el signo informado por DWSIM; la orientación física debe
declararse en `validation_spec.yaml`.

Una propiedad que no pueda extraerse se representa como `null` y, para
corrientes materiales, se añade una advertencia. Nunca se sustituye por cero.

## Timeout del proceso llamador

`CalculateFlowsheet4()` puede quedar bloqueado dentro de código nativo o de un
modelo externo. Por eso el timeout debe aplicarse al **proceso hijo completo**,
un proceso por caso. Ejemplo sin dependencias adicionales:

```python
import subprocess

completed = subprocess.run(
    [
        r"tools\dwsim_automation_runner\bin\DwsimValidationRunner.exe",
        "--simulation",
        simulation_path,
    ],
    capture_output=True,
    text=True,
    timeout=180,
    check=False,
)
```

Si vence el timeout, `subprocess` termina solamente el runner hijo. El llamador
debe registrar `NOT_RUN` o el fallback a datasets; nunca debe presentar ese
fallback como una ejecución de DWSIM.

## Códigos de salida

- `0`: versión compatible, solver sin excepciones, archivo original inalterado
  y todos los objetos solicitados encontrados.
- `1`: error de carga/cálculo/extracción, versión incompatible, checksum
  modificado u objeto solicitado ausente.
- `2`: argumentos inválidos.

Incluso con código `1`, si los argumentos fueron válidos el runner intenta
emitir el JSON de diagnóstico.

## Alcance y limitaciones

La colección `SimulationObjects` es estable; las propiedades concretas varían
entre tipos de equipos y versiones. El contrato mínimo estable es:

- identificación y tipo de objeto;
- indicador de corriente material;
- estado termodinámico y flujo cuando la API los expone;
- energía o deber térmico cuando existe un getter público;
- `null` más advertencia cuando el valor no está disponible.

El validador debe comprobar que los objetos y campos exigidos por
`validation_spec.yaml` existen. Este runner no deduce fronteras de balance, no
clasifica entradas o salidas y no convierte automáticamente el signo de calor o
trabajo.
