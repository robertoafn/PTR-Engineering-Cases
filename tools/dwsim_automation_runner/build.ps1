[CmdletBinding()]
param(
    [Parameter()]
    [string]$DwsimHome,

    [Parameter()]
    [string]$OutputPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Resolve-DwsimHome {
    param([string]$RequestedPath)

    $candidates = [System.Collections.Generic.List[string]]::new()
    if (-not [string]::IsNullOrWhiteSpace($RequestedPath)) {
        $candidates.Add($RequestedPath)
    }
    if (-not [string]::IsNullOrWhiteSpace($env:DWSIM_HOME)) {
        $candidates.Add($env:DWSIM_HOME)
    }
    if (-not [string]::IsNullOrWhiteSpace($env:LOCALAPPDATA)) {
        $candidates.Add((Join-Path $env:LOCALAPPDATA 'DWSIM'))
    }
    if (-not [string]::IsNullOrWhiteSpace($env:ProgramFiles)) {
        $candidates.Add((Join-Path $env:ProgramFiles 'DWSIM'))
    }

    foreach ($candidate in $candidates) {
        try {
            $expanded = [Environment]::ExpandEnvironmentVariables($candidate.Trim().Trim('"'))
            $resolved = [IO.Path]::GetFullPath($expanded)
            $automationDll = Join-Path $resolved 'DWSIM.Automation.dll'
            if ((Test-Path -LiteralPath $resolved -PathType Container) -and
                (Test-Path -LiteralPath $automationDll -PathType Leaf)) {
                return $resolved
            }
        }
        catch {
            # Se prueba el siguiente candidato.
        }
    }

    throw 'No se encontró DWSIM. Indique -DwsimHome o configure DWSIM_HOME.'
}

$compiler = 'C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe'
if (-not (Test-Path -LiteralPath $compiler -PathType Leaf)) {
    throw "No se encontró el compilador x64 requerido: $compiler"
}

$resolvedDwsimHome = Resolve-DwsimHome -RequestedPath $DwsimHome
$sourcePath = Join-Path $PSScriptRoot 'DwsimValidationRunner.cs'
if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) {
    throw "No se encontró el código fuente: $sourcePath"
}

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path $PSScriptRoot 'bin\DwsimValidationRunner.exe'
}
elseif (-not [IO.Path]::IsPathRooted($OutputPath)) {
    $OutputPath = Join-Path (Get-Location) $OutputPath
}

$OutputPath = [IO.Path]::GetFullPath($OutputPath)
$outputDirectory = Split-Path -Parent $OutputPath
if (-not (Test-Path -LiteralPath $outputDirectory -PathType Container)) {
    New-Item -ItemType Directory -Path $outputDirectory -Force | Out-Null
}

$automationReference = Join-Path $resolvedDwsimHome 'DWSIM.Automation.dll'
$interfacesReference = Join-Path $resolvedDwsimHome 'DWSIM.Interfaces.dll'
if (-not (Test-Path -LiteralPath $interfacesReference -PathType Leaf)) {
    throw "No se encontró la referencia requerida: $interfacesReference"
}

$compilerArguments = @(
    '/nologo'
    '/target:exe'
    '/platform:x64'
    '/optimize+'
    '/debug-'
    '/warn:4'
    '/utf8output'
    "/out:$OutputPath"
    "/reference:$automationReference"
    "/reference:$interfacesReference"
    '/reference:System.Runtime.Serialization.dll'
    $sourcePath
)

Write-Host "Compilando runner x64 con DWSIM_HOME=$resolvedDwsimHome"
& $compiler @compilerArguments
if ($LASTEXITCODE -ne 0) {
    throw "csc.exe finalizó con código $LASTEXITCODE."
}

if (-not (Test-Path -LiteralPath $OutputPath -PathType Leaf)) {
    throw "La compilación terminó sin producir $OutputPath."
}

Write-Host "Runner generado: $OutputPath"
