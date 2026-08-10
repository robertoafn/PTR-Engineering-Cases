"""Verifica paridad entre DWSIM Automation API y el dataset del Caso 002.

El runner existente trabaja sobre una copia temporal y este script comprueba
SHA-256 antes y después. La comparación usa el valor publicado en el dataset
como referencia. Códigos de salida: 0 PASS, 1 FAIL, 2 NOT_RUN.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
CASE_002 = ROOT / "cases" / "002_recuperacion_vapor_flash_y_particion_de_volatiles"
DEFAULT_DATASET = CASE_002 / "data" / "process_results_v01.csv"
DEFAULT_SIMULATION = (
    CASE_002
    / "simulations"
    / "dwsim"
    / "002_recuperacion_vapor_flash_y_particion_de_volatiles.dwxmz"
)
DEFAULT_RUNNER = (
    ROOT / "tools" / "dwsim_automation_runner" / "bin" / "DwsimValidationRunner.exe"
)
STATE_COLUMNS = (
    "temperature_K",
    "pressure_Pa",
    "mass_flow_kg_s",
    "specific_enthalpy_kJ_kg",
)
ENERGY_COLUMNS = ("energy_flow_kW",)
REFERENCE_FLOOR = 1.0e-12


class ContractError(ValueError):
    """Falta un insumo o campo requerido para ejecutar la paridad."""


class ExecutionUnavailable(RuntimeError):
    """DWSIM no produjo una resolución comparable."""


class IntegrityError(RuntimeError):
    """El archivo fuente no quedó íntegro durante la ejecución."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def reject_output_collisions(
    output: Path | None, protected_inputs: Mapping[str, Path]
) -> None:
    """Impide reemplazar dataset, simulación o runner con el CSV de salida."""
    if output is None:
        return
    for label, protected in protected_inputs.items():
        if output == protected:
            raise ContractError(
                f"--output colisiona con {label}: {output}. "
                "Seleccione una ruta de salida distinta."
            )


def verify_source_hash(simulation: Path, expected: str, context: str) -> None:
    try:
        actual = sha256(simulation)
    except OSError as exc:
        raise IntegrityError(
            f"no se pudo reverificar el SHA-256 fuente {context}: {exc}"
        ) from exc
    if actual.lower() != expected.lower():
        raise IntegrityError(
            f"el SHA-256 de la simulación cambió {context}: "
            f"esperado={expected}; actual={actual}"
        )


def read_dataset(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise ContractError(f"no existe el dataset del Caso 002: {path}")
    try:
        frame = pd.read_csv(path)
    except (OSError, pd.errors.ParserError) as exc:
        raise ContractError(f"no se pudo leer el dataset del Caso 002: {exc}") from exc
    required = {"object_id", *STATE_COLUMNS, *ENERGY_COLUMNS}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ContractError(f"dataset: faltan columnas: {', '.join(missing)}")
    if frame.empty:
        raise ContractError("dataset: no contiene corrientes")
    if frame["object_id"].isna().any() or frame["object_id"].astype(str).str.strip().eq("").any():
        raise ContractError("dataset: object_id no puede estar vacío")
    if frame["object_id"].astype(str).duplicated().any():
        raise ContractError("dataset: object_id debe ser único")
    numeric_columns = [*STATE_COLUMNS, *ENERGY_COLUMNS]
    frame = frame.copy()
    frame[numeric_columns] = frame[numeric_columns].apply(pd.to_numeric, errors="coerce")
    if not np.isfinite(frame[numeric_columns].to_numpy(dtype=float)).all():
        raise ContractError("dataset: los valores comparados deben ser numéricos y finitos")
    frame["object_id"] = frame["object_id"].astype(str)
    return frame


def _parse_runner_payload(stdout: str) -> Mapping[str, Any]:
    try:
        payload = json.loads(stdout.lstrip("\ufeff").strip())
    except json.JSONDecodeError as exc:
        raise ExecutionUnavailable("el runner no entregó un JSON válido por stdout") from exc
    if not isinstance(payload, dict):
        raise ExecutionUnavailable("el contrato JSON del runner no es un objeto")
    return payload


def run_dwsim(
    *,
    runner: Path,
    simulation: Path,
    object_ids: list[str],
    required_version: str,
    timeout_seconds: float,
    dwsim_home: Path | None,
) -> tuple[Mapping[str, Any], str, str]:
    if not runner.is_file():
        raise ContractError(f"no existe el runner DWSIM compilado: {runner}")
    if not simulation.is_file():
        raise ContractError(f"no existe la simulación del Caso 002: {simulation}")
    before = sha256(simulation)
    command = [
        str(runner),
        "--simulation",
        str(simulation),
        "--required-version",
        required_version,
        "--objects",
        ",".join(object_ids),
    ]
    if dwsim_home is not None:
        command.extend(("--dwsim-home", str(dwsim_home)))
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        after_timeout = sha256(simulation)
        if after_timeout != before:
            raise IntegrityError(
                "el SHA-256 de la simulación cambió durante una ejecución con timeout"
            ) from exc
        raise ExecutionUnavailable(
            f"DWSIM excedió el timeout de {timeout_seconds:g} s"
        ) from exc
    except OSError as exc:
        after_error = sha256(simulation)
        if after_error != before:
            raise IntegrityError(
                "el SHA-256 de la simulación cambió tras un error de ejecución"
            ) from exc
        raise ExecutionUnavailable(f"no se pudo iniciar el runner DWSIM: {exc}") from exc

    after = sha256(simulation)
    if after != before:
        raise IntegrityError("el SHA-256 de la simulación cambió durante la paridad")
    payload = _parse_runner_payload(completed.stdout)
    diagnostic = completed.stderr.strip()
    if completed.returncode != 0:
        errors = payload.get("errors") or []
        raise ExecutionUnavailable(
            "el runner terminó sin una solución comparable "
            f"(código {completed.returncode}; errors={errors}; stderr={diagnostic[:1000]})"
        )
    if payload.get("version_compatible") is not True:
        raise ExecutionUnavailable("la versión DWSIM no coincide con required_version")
    if payload.get("solved") is not True:
        raise ExecutionUnavailable("DWSIM no informó solved=true")
    if payload.get("errors"):
        raise ExecutionUnavailable(f"DWSIM informó errores: {payload['errors']}")
    if payload.get("missing_objects"):
        raise ExecutionUnavailable(
            f"DWSIM no devolvió objetos requeridos: {payload['missing_objects']}"
        )
    if payload.get("source_unchanged") is not True:
        raise IntegrityError("el runner no confirmó source_unchanged=true")
    for field in ("simulation_sha256", "simulation_sha256_after"):
        reported = str(payload.get(field, "")).lower()
        if reported != before.lower():
            raise IntegrityError(f"el runner informó un {field} distinto del archivo fuente")
    return payload, before, diagnostic


def _object_index(payload: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    raw_objects = payload.get("objects")
    if not isinstance(raw_objects, list):
        raise ExecutionUnavailable("el runner no entregó la lista objects")
    index: dict[str, Mapping[str, Any]] = {}
    for raw in raw_objects:
        if not isinstance(raw, dict):
            raise ExecutionUnavailable("objects contiene un elemento que no es un objeto JSON")
        for key in ("object_id", "object_tag"):
            identifier = raw.get(key)
            if identifier is None:
                continue
            text = str(identifier)
            if text in index and index[text] is not raw:
                raise ExecutionUnavailable(f"identificador DWSIM ambiguo: {text}")
            index[text] = raw
    return index


def build_parity_table(
    dataset: pd.DataFrame,
    payload: Mapping[str, Any],
    *,
    state_tolerance_percent: float,
    energy_tolerance_percent: float,
) -> pd.DataFrame:
    index = _object_index(payload)
    rows: list[dict[str, object]] = []
    for _, dataset_row in dataset.iterrows():
        object_id = str(dataset_row["object_id"])
        api_row = index.get(object_id)
        if api_row is None:
            raise ExecutionUnavailable(f"el runner no devolvió el objeto {object_id}")
        for metric in (*STATE_COLUMNS, *ENERGY_COLUMNS):
            api_raw = api_row.get(metric)
            try:
                api_value = float(api_raw)
            except (TypeError, ValueError) as exc:
                raise ExecutionUnavailable(
                    f"el runner no entregó {metric} numérico para {object_id}"
                ) from exc
            if not math.isfinite(api_value):
                raise ExecutionUnavailable(
                    f"el runner no entregó {metric} finito para {object_id}"
                )
            dataset_value = float(dataset_row[metric])
            absolute_difference = abs(api_value - dataset_value)
            denominator = max(abs(dataset_value), REFERENCE_FLOOR)
            relative_difference = absolute_difference / denominator * 100.0
            scope = "energy" if metric in ENERGY_COLUMNS else "state"
            tolerance = (
                energy_tolerance_percent if scope == "energy" else state_tolerance_percent
            )
            rows.append(
                {
                    "object_id": object_id,
                    "metric": metric,
                    "scope": scope,
                    "dataset_value": dataset_value,
                    "api_value": api_value,
                    "absolute_difference": absolute_difference,
                    "relative_difference_percent": relative_difference,
                    "reference_floor": REFERENCE_FLOOR,
                    "tolerance_percent": tolerance,
                    "status": "PASS" if relative_difference <= tolerance else "FAIL",
                }
            )
    return pd.DataFrame(rows)


def _write_csv_atomic(frame: pd.DataFrame, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    frame.to_csv(temporary, index=False, lineterminator="\n")
    temporary.replace(output)


def build_parity_summary(comparison: pd.DataFrame) -> pd.DataFrame:
    """Resume por objeto usando sólo magnitudes adimensionales comparables.

    El detalle largo conserva valores con unidades heterogéneas para el JSON de
    diagnóstico. El CSV versionado usa exclusivamente porcentajes, de modo que
    cada columna tiene una unidad fija y puede gobernarse con un sidecar.
    """
    rows: list[dict[str, object]] = []
    for object_id, group in comparison.groupby("object_id", sort=False):
        state = group[group["scope"] == "state"]
        energy = group[group["scope"] == "energy"]
        state_max = float(state["relative_difference_percent"].max())
        energy_max = float(energy["relative_difference_percent"].max())
        state_tolerance = float(state["tolerance_percent"].max())
        energy_tolerance = float(energy["tolerance_percent"].max())
        failed_metrics = ",".join(
            group.loc[group["status"] == "FAIL", "metric"].astype(str)
        )
        state_status = "PASS" if state_max <= state_tolerance else "FAIL"
        energy_status = "PASS" if energy_max <= energy_tolerance else "FAIL"
        rows.append(
            {
                "object_id": object_id,
                "max_state_difference_percent": state_max,
                "max_energy_difference_percent": energy_max,
                "state_tolerance_percent": state_tolerance,
                "energy_tolerance_percent": energy_tolerance,
                "state_status": state_status,
                "energy_status": energy_status,
                "failed_metrics": failed_metrics,
                "overall_status": (
                    "PASS"
                    if state_status == "PASS" and energy_status == "PASS"
                    else "FAIL"
                ),
            }
        )
    return pd.DataFrame(rows)


def _emit(status: str, message: str, **details: object) -> None:
    print(
        json.dumps(
            {"status": status, "message": message, **details},
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--simulation", type=Path, default=DEFAULT_SIMULATION)
    parser.add_argument("--runner", type=Path, default=DEFAULT_RUNNER)
    parser.add_argument("--dwsim-home", type=Path)
    parser.add_argument("--required-version", default="9.0.5")
    parser.add_argument("--timeout-seconds", type=float, default=180.0)
    parser.add_argument("--state-tolerance-percent", type=float, default=0.05)
    parser.add_argument("--energy-tolerance-percent", type=float, default=0.05)
    parser.add_argument(
        "--output",
        type=Path,
        help="CSV opcional; no se escribe en estados NOT_RUN ni en fallas de integridad.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    dataset_path = args.dataset.resolve()
    simulation_path = args.simulation.resolve()
    runner_path = args.runner.resolve()
    output_path = args.output.resolve() if args.output is not None else None
    dwsim_home = args.dwsim_home.resolve() if args.dwsim_home is not None else None
    numeric_options = (
        args.timeout_seconds,
        args.state_tolerance_percent,
        args.energy_tolerance_percent,
    )
    if (
        not all(math.isfinite(value) for value in numeric_options)
        or args.timeout_seconds <= 0.0
        or args.state_tolerance_percent < 0.0
        or args.energy_tolerance_percent < 0.0
    ):
        _emit(
            "NOT_RUN",
            "Timeout y tolerancias deben ser finitos; timeout > 0 y tolerancias >= 0.",
            output_written=False,
        )
        return 2

    try:
        reject_output_collisions(
            output_path,
            {
                "--dataset": dataset_path,
                "--simulation": simulation_path,
                "--runner": runner_path,
            },
        )
        dataset = read_dataset(dataset_path)
        payload, source_hash, stderr = run_dwsim(
            runner=runner_path,
            simulation=simulation_path,
            object_ids=dataset["object_id"].tolist(),
            required_version=args.required_version,
            timeout_seconds=args.timeout_seconds,
            dwsim_home=dwsim_home,
        )
        comparison = build_parity_table(
            dataset,
            payload,
            state_tolerance_percent=args.state_tolerance_percent,
            energy_tolerance_percent=args.energy_tolerance_percent,
        )
    except IntegrityError as exc:
        _emit(
            "FAIL",
            str(exc),
            dataset_csv=str(dataset_path),
            simulation=str(simulation_path),
            output_written=False,
        )
        return 1
    except (ContractError, ExecutionUnavailable) as exc:
        _emit(
            "NOT_RUN",
            str(exc),
            dataset_csv=str(dataset_path),
            simulation=str(simulation_path),
            runner=str(runner_path),
            output_written=False,
        )
        return 2

    overall = "PASS" if (comparison["status"] == "PASS").all() else "FAIL"
    output_written = False
    try:
        verify_source_hash(simulation_path, source_hash, "antes de escribir la salida")
        if output_path is not None:
            _write_csv_atomic(build_parity_summary(comparison), output_path)
            output_written = True
    except IntegrityError as exc:
        _emit(
            "FAIL",
            str(exc),
            dataset_csv=str(dataset_path),
            simulation=str(simulation_path),
            output_written=output_written,
        )
        return 1
    except Exception:
        # Una falla de escritura no elimina la obligación de comprobar la fuente.
        verify_source_hash(
            simulation_path,
            source_hash,
            "después de una escritura fallida",
        )
        raise

    try:
        verify_source_hash(
            simulation_path,
            source_hash,
            "después de escribir la salida",
        )
    except IntegrityError as exc:
        _emit(
            "FAIL",
            str(exc),
            dataset_csv=str(dataset_path),
            simulation=str(simulation_path),
            output_written=output_written,
        )
        return 1
    state_rows = comparison[comparison["scope"] == "state"]
    energy_rows = comparison[comparison["scope"] == "energy"]
    failed = comparison[comparison["status"] == "FAIL"]
    _emit(
        overall,
        "Paridad API-dataset ejecutada sin modificar la simulación fuente.",
        simulation_sha256=source_hash,
        dwsim_version=payload.get("dwsim_version"),
        source_unchanged=True,
        max_state_difference_percent=float(state_rows["relative_difference_percent"].max()),
        max_energy_difference_percent=float(energy_rows["relative_difference_percent"].max()),
        state_tolerance_percent=float(args.state_tolerance_percent),
        energy_tolerance_percent=float(args.energy_tolerance_percent),
        failed_comparisons=failed.to_dict(orient="records"),
        runner_stderr=stderr[:4000],
        output_csv=str(output_path) if output_path is not None else None,
        output_written=output_written,
    )
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
