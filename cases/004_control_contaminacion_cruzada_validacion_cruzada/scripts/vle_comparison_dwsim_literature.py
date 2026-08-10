"""Compara una curva VLE DWSIM con datos experimentales trazables.

El script no descarga ni incorpora datos de literatura. Los dos CSV deben
declarar componentes, fuente, presión, temperatura y fracciones molares. La
curva DWSIM se interpola linealmente como T(x), y(x), T(y) y x(y), sin
extrapolación. Si faltan insumos o el contrato no es comparable se informa
``NOT_RUN`` (código 2) y no se crea el CSV de resultados.

Columnas obligatorias en ambos CSV:

``source_id, component_1, component_2, temperature_K, pressure_Pa,
x_component_1_molfrac, y_component_1_molfrac``.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path

import numpy as np
import pandas as pd

CASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_LITERATURE = (
    CASE_DIR / "data" / "raw" / "literature" / "vle_meoh_h2o_experimental_v01.csv"
)
DEFAULT_DWSIM = CASE_DIR / "data" / "processed" / "vle_dwsim_v01.csv"
DEFAULT_OUTPUT = CASE_DIR / "data" / "processed" / "vle_meoh_h2o_comparison_v01.csv"
REQUIRED_COLUMNS = {
    "source_id",
    "component_1",
    "component_2",
    "temperature_K",
    "pressure_Pa",
    "x_component_1_molfrac",
    "y_component_1_molfrac",
}


class ContractError(ValueError):
    """El insumo no permite una comparación VLE inequívoca."""


def _normalise(value: object) -> str:
    return " ".join(str(value).strip().lower().split())


def read_curve(path: Path, label: str) -> pd.DataFrame:
    if not path.is_file():
        raise ContractError(f"no existe el CSV {label}: {path}")
    try:
        frame = pd.read_csv(path)
    except (OSError, pd.errors.ParserError) as exc:
        raise ContractError(f"no se pudo leer el CSV {label}: {exc}") from exc
    missing = sorted(REQUIRED_COLUMNS.difference(frame.columns))
    if missing:
        raise ContractError(f"{label}: faltan columnas obligatorias: {', '.join(missing)}")
    if frame.empty:
        raise ContractError(f"{label}: el CSV no contiene observaciones")
    if frame[list(REQUIRED_COLUMNS)].isna().any().any():
        raise ContractError(f"{label}: hay valores obligatorios vacíos")

    frame = frame.copy()
    numeric_columns = [
        "temperature_K",
        "pressure_Pa",
        "x_component_1_molfrac",
        "y_component_1_molfrac",
    ]
    frame[numeric_columns] = frame[numeric_columns].apply(pd.to_numeric, errors="coerce")
    if not np.isfinite(frame[numeric_columns].to_numpy(dtype=float)).all():
        raise ContractError(f"{label}: todos los valores numéricos deben ser finitos")
    if (frame["temperature_K"] <= 0.0).any() or (frame["pressure_Pa"] <= 0.0).any():
        raise ContractError(f"{label}: temperatura y presión deben ser positivas")
    for column in ("x_component_1_molfrac", "y_component_1_molfrac"):
        if not frame[column].between(0.0, 1.0).all():
            raise ContractError(f"{label}: {column} debe estar en [0, 1]")
    if frame["source_id"].astype(str).str.strip().eq("").any():
        raise ContractError(f"{label}: source_id no puede estar vacío")
    return frame


def _single_identity(frame: pd.DataFrame, column: str, label: str) -> str:
    normalised = frame[column].astype(str).map(_normalise)
    values = normalised.unique()
    if len(values) != 1 or not values[0]:
        raise ContractError(f"{label}: {column} debe identificar un único componente")
    return values[0]


def _check_comparability(
    literature: pd.DataFrame,
    dwsim: pd.DataFrame,
    pressure_tolerance_pa: float,
) -> tuple[str, str, float, float]:
    lit_c1 = _single_identity(literature, "component_1", "literatura")
    lit_c2 = _single_identity(literature, "component_2", "literatura")
    sim_c1 = _single_identity(dwsim, "component_1", "DWSIM")
    sim_c2 = _single_identity(dwsim, "component_2", "DWSIM")
    if lit_c1 != sim_c1 or lit_c2 != sim_c2:
        raise ContractError(
            "el orden de componentes de la literatura no coincide con la curva DWSIM"
        )
    if lit_c1 == lit_c2:
        raise ContractError("los componentes 1 y 2 deben ser distintos")

    p_lit = literature["pressure_Pa"].to_numpy(dtype=float)
    p_sim = dwsim["pressure_Pa"].to_numpy(dtype=float)
    if np.ptp(p_lit) > pressure_tolerance_pa:
        raise ContractError(
            "literatura: la presión no es isobárica dentro de la tolerancia declarada"
        )
    if np.ptp(p_sim) > pressure_tolerance_pa:
        raise ContractError(
            "DWSIM: la presión no es isobárica dentro de la tolerancia declarada"
        )
    mean_lit = float(np.mean(p_lit))
    mean_sim = float(np.mean(p_sim))
    if abs(mean_lit - mean_sim) > pressure_tolerance_pa:
        raise ContractError(
            "las presiones medias de literatura y DWSIM no son comparables: "
            f"{mean_lit:.9g} Pa frente a {mean_sim:.9g} Pa"
        )
    return lit_c1, lit_c2, mean_lit, mean_sim


def _strict_curve(frame: pd.DataFrame, coordinate: str) -> pd.DataFrame:
    ordered = frame.sort_values(coordinate, kind="mergesort").reset_index(drop=True)
    values = ordered[coordinate].to_numpy(dtype=float)
    if len(values) < 2 or not (np.diff(values) > 0.0).all():
        raise ContractError(
            f"DWSIM: {coordinate} debe ser estrictamente creciente y tener al menos 2 puntos"
        )
    return ordered


def build_comparison(
    literature: pd.DataFrame,
    dwsim: pd.DataFrame,
    *,
    temperature_tolerance_k: float,
    composition_tolerance: float,
    pressure_tolerance_pa: float,
) -> pd.DataFrame:
    component_1, component_2, p_lit, p_sim = _check_comparability(
        literature, dwsim, pressure_tolerance_pa
    )
    by_x = _strict_curve(dwsim, "x_component_1_molfrac")
    by_y = _strict_curve(dwsim, "y_component_1_molfrac")

    x_lit = literature["x_component_1_molfrac"].to_numpy(dtype=float)
    y_lit = literature["y_component_1_molfrac"].to_numpy(dtype=float)
    x_sim = by_x["x_component_1_molfrac"].to_numpy(dtype=float)
    y_sim_at_x_grid = by_x["y_component_1_molfrac"].to_numpy(dtype=float)
    temperature_x_grid = by_x["temperature_K"].to_numpy(dtype=float)
    y_sim = by_y["y_component_1_molfrac"].to_numpy(dtype=float)
    x_sim_at_y_grid = by_y["x_component_1_molfrac"].to_numpy(dtype=float)
    temperature_y_grid = by_y["temperature_K"].to_numpy(dtype=float)

    epsilon = 1.0e-12
    if x_lit.min() < x_sim.min() - epsilon or x_lit.max() > x_sim.max() + epsilon:
        raise ContractError("literatura: x queda fuera de la curva DWSIM; no se extrapola")
    if y_lit.min() < y_sim.min() - epsilon or y_lit.max() > y_sim.max() + epsilon:
        raise ContractError("literatura: y queda fuera de la curva DWSIM; no se extrapola")

    temperature_dwsim_at_x = np.interp(x_lit, x_sim, temperature_x_grid)
    y_dwsim_at_x = np.interp(x_lit, x_sim, y_sim_at_x_grid)
    temperature_dwsim_at_y = np.interp(y_lit, y_sim, temperature_y_grid)
    x_dwsim_at_y = np.interp(y_lit, y_sim, x_sim_at_y_grid)
    temperature_lit = literature["temperature_K"].to_numpy(dtype=float)

    temperature_error_at_x = np.abs(temperature_dwsim_at_x - temperature_lit)
    temperature_error_at_y = np.abs(temperature_dwsim_at_y - temperature_lit)
    temperature_error = np.maximum(temperature_error_at_x, temperature_error_at_y)
    x_error = np.abs(x_dwsim_at_y - x_lit)
    y_error = np.abs(y_dwsim_at_x - y_lit)
    passed = (
        (temperature_error <= temperature_tolerance_k)
        & (x_error <= composition_tolerance)
        & (y_error <= composition_tolerance)
    )

    return pd.DataFrame(
        {
            "literature_source_id": literature["source_id"].astype(str).to_numpy(),
            "dwsim_source_id": str(dwsim["source_id"].iloc[0]),
            "component_1": component_1,
            "component_2": component_2,
            "literature_pressure_mean_Pa": p_lit,
            "dwsim_pressure_mean_Pa": p_sim,
            "temperature_literature_K": temperature_lit,
            "x_literature_molfrac": x_lit,
            "y_literature_molfrac": y_lit,
            "temperature_dwsim_at_x_K": temperature_dwsim_at_x,
            "temperature_dwsim_at_y_K": temperature_dwsim_at_y,
            "x_dwsim_at_y_molfrac": x_dwsim_at_y,
            "y_dwsim_at_x_molfrac": y_dwsim_at_x,
            "abs_temperature_error_at_x_K": temperature_error_at_x,
            "abs_temperature_error_at_y_K": temperature_error_at_y,
            "max_abs_temperature_error_K": temperature_error,
            "abs_x_error_molfrac": x_error,
            "abs_y_error_molfrac": y_error,
            "temperature_tolerance_K": temperature_tolerance_k,
            "composition_tolerance_molfrac": composition_tolerance,
            "interpolation_method": "linear_without_extrapolation",
            "status": np.where(passed, "PASS", "FAIL"),
        }
    )


def _write_csv_atomic(frame: pd.DataFrame, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        dir=output.parent,
        prefix=f".{output.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        temporary = Path(handle.name)
    try:
        frame.to_csv(temporary, index=False, lineterminator="\n")
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)


def _emit(status: str, message: str, **details: object) -> None:
    print(
        json.dumps(
            {"status": status, "message": message, **details},
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )
    )


def _resolve_contract_paths(
    literature: Path,
    dwsim: Path,
    output: Path,
) -> tuple[Path, Path, Path]:
    resolved = (
        literature.expanduser().resolve(),
        dwsim.expanduser().resolve(),
        output.expanduser().resolve(),
    )
    labels = ("--literature", "--dwsim", "--output")
    for label, path in zip(labels, resolved, strict=True):
        if path.suffix.lower() != ".csv":
            raise ContractError(f"{label} debe apuntar a un archivo .csv")
    for left in range(len(resolved)):
        for right in range(left + 1, len(resolved)):
            same_file = resolved[left] == resolved[right]
            if not same_file:
                try:
                    same_file = os.path.samefile(resolved[left], resolved[right])
                except OSError:
                    same_file = False
            if same_file:
                raise ContractError(
                    f"la ruta de {labels[left]} colisiona con {labels[right]}"
                )
    return resolved


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--literature", type=Path, default=DEFAULT_LITERATURE)
    parser.add_argument("--dwsim", type=Path, default=DEFAULT_DWSIM)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--temperature-tolerance-K", type=float, default=0.01)
    parser.add_argument("--composition-tolerance", type=float, default=0.01)
    parser.add_argument("--pressure-tolerance-Pa", type=float, default=100.0)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    tolerances = (
        args.temperature_tolerance_K,
        args.composition_tolerance,
        args.pressure_tolerance_Pa,
    )
    if not all(math.isfinite(value) and value >= 0.0 for value in tolerances):
        _emit(
            "NOT_RUN",
            "Todas las tolerancias deben ser finitas y no negativas.",
            output_written=False,
        )
        return 2
    try:
        literature_path, dwsim_path, output_path = _resolve_contract_paths(
            args.literature,
            args.dwsim,
            args.output,
        )
        literature = read_curve(literature_path, "literatura")
        dwsim = read_curve(dwsim_path, "DWSIM")
        comparison = build_comparison(
            literature,
            dwsim,
            temperature_tolerance_k=args.temperature_tolerance_K,
            composition_tolerance=args.composition_tolerance,
            pressure_tolerance_pa=args.pressure_tolerance_Pa,
        )
    except ContractError as exc:
        _emit(
            "NOT_RUN",
            str(exc),
            literature_csv=str(args.literature.expanduser().resolve()),
            dwsim_csv=str(args.dwsim.expanduser().resolve()),
            output_csv=str(args.output.expanduser().resolve()),
            output_written=False,
        )
        return 2

    overall = "PASS" if (comparison["status"] == "PASS").all() else "FAIL"
    _write_csv_atomic(comparison, output_path)
    _emit(
        overall,
        "Comparación VLE ejecutada con fuentes y estado termodinámico explícitos.",
        rows=int(len(comparison)),
        max_abs_temperature_error_K=float(comparison["max_abs_temperature_error_K"].max()),
        max_abs_x_error_molfrac=float(comparison["abs_x_error_molfrac"].max()),
        max_abs_y_error_molfrac=float(comparison["abs_y_error_molfrac"].max()),
        output_csv=str(output_path),
        output_written=True,
    )
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
