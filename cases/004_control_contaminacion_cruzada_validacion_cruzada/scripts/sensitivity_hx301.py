"""Genera la malla de sensibilidad reproducible del intercambiador HX-301.

Cada escenario se resuelve en un proceso DWSIM independiente. El runner trabaja
sobre una copia temporal del ``.dwxmz`` y nunca guarda el flowsheet modificado.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import subprocess
import sys
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

U_VALUES_W_M2_K = (800.0, 1000.0, 1200.0, 1500.0)
COLD_FLOW_FACTORS = (0.8, 1.0, 1.2)
REQUIRED_DWSIM_VERSION = "9.0.5"

HOT_IN_TAG = "MSTR-301_CONDENSADO_CALIENTE"
COLD_IN_TAG = "MSTR-302_AGUA_FRIA"
HX_TAG = "HX-301_INTERCAMBIADOR"
HOT_OUT_TAG = "MSTR-303_CONDENSADO_ENFRIADO"
COLD_OUT_TAG = "MSTR-304_AGUA_PRECALENTADA"
OBJECT_TAGS = (HOT_IN_TAG, COLD_IN_TAG, HX_TAG, HOT_OUT_TAG, COLD_OUT_TAG)

CASE_DIR = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SIMULATION = (
    CASE_DIR
    / "simulations"
    / "dwsim"
    / "004_control_contaminacion_cruzada_validacion_cruzada.dwxmz"
)
DEFAULT_RUNNER = (
    REPOSITORY_ROOT
    / "tools"
    / "dwsim_automation_runner"
    / "bin"
    / "DwsimValidationRunner.exe"
)
DEFAULT_OUTPUT = CASE_DIR / "data" / "processed" / "hx301_sensitivity_v01.csv"

CSV_COLUMNS = (
    "scenario_id",
    "overall_coefficient_W_m2_K",
    "cold_flow_factor",
    "area_m2",
    "ua_W_K",
    "hot_inlet_temperature_K",
    "cold_inlet_temperature_K",
    "hot_outlet_temperature_K",
    "cold_outlet_temperature_K",
    "hot_inlet_pressure_Pa",
    "cold_inlet_pressure_Pa",
    "clean_to_contaminated_deltaP_Pa",
    "hot_mass_flow_kg_s",
    "cold_mass_flow_kg_s",
    "heat_duty_kW",
    "lmtd_K",
    "q_hot_kW",
    "q_cold_kW",
    "energy_balance_residual_kW",
    "energy_balance_relative_percent",
    "source_sha256",
    "dwsim_version",
)


class SensitivityError(RuntimeError):
    """Indica que un escenario no produjo evidencia API válida."""


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Resuelve la malla U x factor de caudal frío del HX-301 mediante "
            "DWSIM Automation API."
        )
    )
    parser.add_argument("--simulation", type=Path, default=DEFAULT_SIMULATION)
    parser.add_argument("--runner", type=Path, default=DEFAULT_RUNNER)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--dwsim-home", type=Path)
    parser.add_argument("--timeout", type=float, default=180.0)
    return parser


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _reject_output_collisions(
    output: Path, protected_inputs: Mapping[str, Path]
) -> None:
    """Impide que la escritura CSV reemplace una entrada ejecutable o científica."""
    for label, protected in protected_inputs.items():
        if output == protected:
            raise SensitivityError(
                f"--output colisiona con {label}: {output}. "
                "Seleccione una ruta de salida distinta."
            )


def _verify_source_hash(simulation: Path, expected: str, context: str) -> None:
    try:
        actual = _sha256(simulation)
    except OSError as error:
        raise SensitivityError(
            f"No se pudo reverificar el SHA-256 fuente {context}: {error}"
        ) from error
    if actual.lower() != expected.lower():
        raise SensitivityError(
            f"El SHA-256 del .dwxmz fuente cambió {context}: "
            f"esperado={expected}; actual={actual}."
        )


def _verify_runner_hashes(payload: Mapping[str, Any], expected: str) -> None:
    for field in ("simulation_sha256", "simulation_sha256_after"):
        reported = str(payload.get(field, "")).lower()
        if reported != expected.lower():
            raise SensitivityError(
                f"El runner informó {field}={reported or '<vacío>'}; "
                f"se esperaba {expected}."
            )


def _finite_number(value: Any, field: str) -> float:
    if value is None:
        raise SensitivityError(f"DWSIM no informó {field}.")
    try:
        converted = float(value)
    except (TypeError, ValueError) as error:
        raise SensitivityError(f"{field} no es numérico: {value!r}.") from error
    if not math.isfinite(converted):
        raise SensitivityError(f"{field} no es finito: {value!r}.")
    return converted


def _equivalent(actual: float, expected: float) -> bool:
    tolerance = max(1.0e-9, abs(expected) * 1.0e-9)
    return abs(actual - expected) <= tolerance


def _objects_by_tag(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    objects = payload.get("objects")
    if not isinstance(objects, list):
        raise SensitivityError("El runner no devolvió una lista de objetos.")
    by_tag = {
        str(item.get("object_tag")): item
        for item in objects
        if isinstance(item, dict) and item.get("object_tag")
    }
    missing = [tag for tag in OBJECT_TAGS if tag not in by_tag]
    if missing:
        raise SensitivityError(
            "Faltan objetos requeridos en la respuesta API: " + ", ".join(missing)
        )
    return by_tag


def _diagnostic_message(
    command: list[str], completed: subprocess.CompletedProcess[str]
) -> str:
    parts = [
        f"comando={subprocess.list2cmdline(command)}",
        f"exit_code={completed.returncode}",
    ]
    if completed.stderr.strip():
        parts.append(f"stderr={completed.stderr.strip()}")
    if completed.stdout.strip():
        parts.append(f"stdout={completed.stdout.strip()}")
    return " | ".join(parts)


def _run_scenario(
    *,
    runner: Path,
    simulation: Path,
    dwsim_home: Path | None,
    timeout_seconds: float,
    u_value: float,
    cold_flow_factor: float,
) -> dict[str, Any]:
    command = [
        str(runner),
        "--simulation",
        str(simulation),
        "--required-version",
        REQUIRED_DWSIM_VERSION,
        "--objects",
        ",".join(OBJECT_TAGS),
        "--set-overall-coefficient",
        f"{HX_TAG}={u_value:.15g}",
        "--set-mass-flow-factor",
        f"{COLD_IN_TAG}={cold_flow_factor:.15g}",
    ]
    if dwsim_home is not None:
        command.extend(["--dwsim-home", str(dwsim_home)])

    creation_flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            check=False,
            cwd=CASE_DIR,
            creationflags=creation_flags,
        )
    except subprocess.TimeoutExpired as error:
        raise SensitivityError(
            f"DWSIM excedió {timeout_seconds:g} s para "
            f"U={u_value:g}, factor={cold_flow_factor:g}."
        ) from error

    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise SensitivityError(
            "El runner no devolvió JSON válido: "
            + _diagnostic_message(command, completed)
        ) from error

    if completed.returncode != 0:
        raise SensitivityError(
            "El escenario DWSIM falló: " + _diagnostic_message(command, completed)
        )
    if payload.get("solved") is not True:
        raise SensitivityError(f"El solver no confirmó convergencia: {payload['errors']!r}")
    if payload.get("source_unchanged") is not True:
        raise SensitivityError("El runner no confirmó la inmutabilidad del .dwxmz fuente.")
    if payload.get("version_compatible") is not True:
        raise SensitivityError(
            f"Versión DWSIM incompatible: {payload.get('dwsim_version')!r}."
        )
    return payload


def _scenario_row(
    scenario_id: str,
    u_value: float,
    cold_flow_factor: float,
    payload: dict[str, Any],
) -> dict[str, Any]:
    objects = _objects_by_tag(payload)
    hot_in = objects[HOT_IN_TAG]
    cold_in = objects[COLD_IN_TAG]
    exchanger = objects[HX_TAG]
    hot_out = objects[HOT_OUT_TAG]
    cold_out = objects[COLD_OUT_TAG]

    actual_u = _finite_number(
        exchanger.get("overall_coefficient_W_m2_K"),
        "overall_coefficient_W_m2_K",
    )
    area = _finite_number(exchanger.get("area_m2"), "area_m2")
    lmtd = _finite_number(exchanger.get("lmtd_K"), "lmtd_K")
    duty = _finite_number(exchanger.get("duty_kW"), "duty_kW")
    if not _equivalent(actual_u, u_value):
        raise SensitivityError(
            f"U aplicada ({actual_u:g}) no coincide con U solicitada ({u_value:g})."
        )

    hot_in_temperature = _finite_number(hot_in.get("temperature_K"), "T hot in")
    cold_in_temperature = _finite_number(cold_in.get("temperature_K"), "T cold in")
    hot_out_temperature = _finite_number(hot_out.get("temperature_K"), "T hot out")
    cold_out_temperature = _finite_number(
        cold_out.get("temperature_K"), "T cold out"
    )
    hot_in_pressure = _finite_number(hot_in.get("pressure_Pa"), "P hot in")
    cold_in_pressure = _finite_number(cold_in.get("pressure_Pa"), "P cold in")
    hot_mass_flow = _finite_number(hot_in.get("mass_flow_kg_s"), "m hot")
    cold_mass_flow = _finite_number(cold_in.get("mass_flow_kg_s"), "m cold")
    hot_in_enthalpy = _finite_number(
        hot_in.get("specific_enthalpy_kJ_kg"), "h hot in"
    )
    hot_out_enthalpy = _finite_number(
        hot_out.get("specific_enthalpy_kJ_kg"), "h hot out"
    )
    cold_in_enthalpy = _finite_number(
        cold_in.get("specific_enthalpy_kJ_kg"), "h cold in"
    )
    cold_out_enthalpy = _finite_number(
        cold_out.get("specific_enthalpy_kJ_kg"), "h cold out"
    )

    q_hot = hot_mass_flow * (hot_in_enthalpy - hot_out_enthalpy)
    q_cold = cold_mass_flow * (cold_out_enthalpy - cold_in_enthalpy)
    residual = abs(q_hot - q_cold)
    mean_duty = (abs(q_hot) + abs(q_cold)) / 2.0
    relative_residual = 100.0 * residual / mean_duty if mean_duty else 0.0

    changes = payload.get("applied_changes")
    if not isinstance(changes, list) or len(changes) != 2:
        raise SensitivityError("El runner no documentó los dos cambios de escenario.")
    mass_change = next(
        (item for item in changes if item.get("kind") == "mass_flow_factor"), None
    )
    if not isinstance(mass_change, dict):
        raise SensitivityError("Falta la trazabilidad del factor de caudal frío.")
    target_cold_flow = _finite_number(mass_change.get("target_value"), "target m cold")
    if not _equivalent(cold_mass_flow, target_cold_flow):
        raise SensitivityError(
            "El caudal frío resuelto no coincide con el cambio aplicado por el runner."
        )

    return {
        "scenario_id": scenario_id,
        "overall_coefficient_W_m2_K": actual_u,
        "cold_flow_factor": cold_flow_factor,
        "area_m2": area,
        "ua_W_K": actual_u * area,
        "hot_inlet_temperature_K": hot_in_temperature,
        "cold_inlet_temperature_K": cold_in_temperature,
        "hot_outlet_temperature_K": hot_out_temperature,
        "cold_outlet_temperature_K": cold_out_temperature,
        "hot_inlet_pressure_Pa": hot_in_pressure,
        "cold_inlet_pressure_Pa": cold_in_pressure,
        "clean_to_contaminated_deltaP_Pa": cold_in_pressure - hot_in_pressure,
        "hot_mass_flow_kg_s": hot_mass_flow,
        "cold_mass_flow_kg_s": cold_mass_flow,
        "heat_duty_kW": duty,
        "lmtd_K": lmtd,
        "q_hot_kW": q_hot,
        "q_cold_kW": q_cold,
        "energy_balance_residual_kW": residual,
        "energy_balance_relative_percent": relative_residual,
        "source_sha256": payload.get("simulation_sha256"),
        "dwsim_version": payload.get("dwsim_version"),
    }


def _csv_value(value: Any) -> Any:
    if isinstance(value, float):
        return format(value, ".15g")
    return value


def _write_csv(output: Path, rows: list[dict[str, Any]]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            newline="",
            delete=False,
            dir=output.parent,
            prefix=output.name + ".",
            suffix=".tmp",
        ) as temporary:
            temporary_path = Path(temporary.name)
            writer = csv.DictWriter(temporary, fieldnames=CSV_COLUMNS, lineterminator="\n")
            writer.writeheader()
            for row in rows:
                writer.writerow({key: _csv_value(row[key]) for key in CSV_COLUMNS})
        temporary_path.replace(output)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def main(argv: Sequence[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = _parser().parse_args(argv)
    runner = args.runner.resolve()
    simulation = args.simulation.resolve()
    output = args.output.resolve()
    dwsim_home = args.dwsim_home.resolve() if args.dwsim_home else None

    _reject_output_collisions(
        output,
        {
            "--simulation": simulation,
            "--runner": runner,
        },
    )

    if not runner.is_file():
        raise SensitivityError(f"No existe el runner DWSIM: {runner}")
    if not simulation.is_file() or simulation.suffix.lower() != ".dwxmz":
        raise SensitivityError(f"Simulación DWSIM no válida: {simulation}")
    if dwsim_home is not None and not (dwsim_home / "DWSIM.Automation.dll").is_file():
        raise SensitivityError(f"DWSIM_HOME no válido: {dwsim_home}")
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        raise SensitivityError("--timeout debe ser un número finito positivo.")

    source_sha256 = _sha256(simulation)

    rows: list[dict[str, Any]] = []
    scenario_number = 0
    for u_value in U_VALUES_W_M2_K:
        for cold_flow_factor in COLD_FLOW_FACTORS:
            scenario_number += 1
            scenario_id = f"S{scenario_number:03d}"
            print(
                f"[{scenario_id}] U={u_value:g} W/(m²·K), "
                f"factor caudal frío={cold_flow_factor:g}",
                flush=True,
            )
            try:
                payload = _run_scenario(
                    runner=runner,
                    simulation=simulation,
                    dwsim_home=dwsim_home,
                    timeout_seconds=args.timeout,
                    u_value=u_value,
                    cold_flow_factor=cold_flow_factor,
                )
            finally:
                _verify_source_hash(
                    simulation,
                    source_sha256,
                    f"durante el escenario {scenario_id}",
                )
            _verify_runner_hashes(payload, source_sha256)
            rows.append(
                _scenario_row(
                    scenario_id,
                    u_value,
                    cold_flow_factor,
                    payload,
                )
            )

    _verify_source_hash(simulation, source_sha256, "antes de escribir el CSV")
    try:
        _write_csv(output, rows)
    finally:
        _verify_source_hash(simulation, source_sha256, "después de escribir el CSV")
    print(f"Malla completada: {len(rows)} escenarios -> {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
