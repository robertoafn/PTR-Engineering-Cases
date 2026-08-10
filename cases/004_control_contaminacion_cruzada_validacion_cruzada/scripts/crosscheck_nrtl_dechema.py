"""Contraste reproducible de coeficientes de actividad NRTL.

El script no incorpora parámetros DECHEMA ni puntos DWSIM. Ambos son insumos
externos y trazables. Si el contrato de cualquiera de los CSV está incompleto,
se informa ``NOT_RUN`` (código 2) y no se escribe el CSV de resultados.

Contrato del CSV de parámetros (exactamente una fila):

``source_id, model, component_1, component_2, component_order, convention,
temperature_unit, A_unit, B_unit, A12, A21, B12, B21, alpha12, alpha21``.

Convenciones admitidas:

* ``tau_ij=A_ij+B_ij/T_K`` con A adimensional y B en K.
* ``tau_ij=(A_ij+B_ij*T_K)/(R*T_K)`` con A en J/mol y B en
  J/(mol*K).

``component_order`` debe declarar ``1=<component_1>;2=<component_2>``.

Contrato del CSV DWSIM:

``component_1, component_2, temperature_K, x_component_1,
gamma_component_1_dwsim, gamma_component_2_dwsim``.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

CASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_PARAMETERS = (
    CASE_DIR / "data" / "raw" / "literature" / "dechema_nrtl_meoh_h2o_v01.csv"
)
DEFAULT_DWSIM_POINTS = CASE_DIR / "data" / "processed" / "nrtl_dwsim_points_v01.csv"
DEFAULT_OUTPUT = CASE_DIR / "data" / "processed" / "nrtl_activity_crosscheck_v01.csv"
R_J_MOL_K = 8.31446261815324


class ContractError(ValueError):
    """El insumo no permite ejecutar una comparación inequívoca."""


@dataclass(frozen=True)
class NrtlParameters:
    source_id: str
    component_1: str
    component_2: str
    convention: str
    a12: float
    a21: float
    b12: float
    b21: float
    alpha12: float
    alpha21: float


def _normalise(value: object) -> str:
    return "".join(str(value).strip().lower().split())


def _require_columns(frame: pd.DataFrame, required: set[str], label: str) -> None:
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ContractError(f"{label}: faltan columnas obligatorias: {', '.join(missing)}")


def _finite_number(value: object, field: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ContractError(f"parámetros: {field} no es numérico") from exc
    if not math.isfinite(number):
        raise ContractError(f"parámetros: {field} debe ser finito")
    return number


def read_parameter_contract(path: Path) -> NrtlParameters:
    if not path.is_file():
        raise ContractError(f"no existe el CSV de parámetros: {path}")
    try:
        frame = pd.read_csv(path)
    except (OSError, pd.errors.ParserError) as exc:
        raise ContractError(f"no se pudo leer el CSV de parámetros: {exc}") from exc

    required = {
        "source_id",
        "model",
        "component_1",
        "component_2",
        "component_order",
        "convention",
        "temperature_unit",
        "A_unit",
        "B_unit",
        "A12",
        "A21",
        "B12",
        "B21",
        "alpha12",
        "alpha21",
    }
    _require_columns(frame, required, "parámetros")
    if len(frame) != 1:
        raise ContractError("parámetros: se requiere exactamente una fila por ejecución")
    row = frame.iloc[0]
    if row[list(required)].isna().any():
        raise ContractError("parámetros: hay valores obligatorios vacíos")
    if _normalise(row["model"]) != "nrtl":
        raise ContractError("parámetros: model debe ser NRTL")

    component_1 = str(row["component_1"]).strip()
    component_2 = str(row["component_2"]).strip()
    if not component_1 or not component_2 or _normalise(component_1) == _normalise(component_2):
        raise ContractError("parámetros: los dos componentes deben ser distintos y explícitos")
    expected_order = _normalise(f"1={component_1};2={component_2}")
    if _normalise(row["component_order"]) != expected_order:
        raise ContractError(
            "parámetros: component_order debe ser "
            f"'1={component_1};2={component_2}'"
        )
    if _normalise(row["temperature_unit"]) not in {"k", "kelvin"}:
        raise ContractError("parámetros: temperature_unit debe ser K")

    convention = str(row["convention"]).strip()
    convention_key = _normalise(convention)
    if convention_key == _normalise("tau_ij=A_ij+B_ij/T_K"):
        if _normalise(row["A_unit"]) not in {"dimensionless", "1", "adimensional"}:
            raise ContractError("parámetros: esta convención exige A_unit=dimensionless")
        if _normalise(row["B_unit"]) not in {"k", "kelvin"}:
            raise ContractError("parámetros: esta convención exige B_unit=K")
        canonical_convention = "tau_ij=A_ij+B_ij/T_K"
    elif convention_key == _normalise("tau_ij=(A_ij+B_ij*T_K)/(R*T_K)"):
        if _normalise(row["A_unit"]) not in {"j/mol", "jmol^-1", "jmol-1"}:
            raise ContractError("parámetros: esta convención exige A_unit=J/mol")
        if _normalise(row["B_unit"]) not in {
            "j/(mol*k)",
            "j/mol/k",
            "jmol^-1k^-1",
            "jmol-1k-1",
        }:
            raise ContractError("parámetros: esta convención exige B_unit=J/(mol*K)")
        canonical_convention = "tau_ij=(A_ij+B_ij*T_K)/(R*T_K)"
    else:
        raise ContractError(
            "parámetros: convención NRTL no admitida; debe declararse una de las "
            "dos convenciones documentadas por el script"
        )

    alpha12 = _finite_number(row["alpha12"], "alpha12")
    alpha21 = _finite_number(row["alpha21"], "alpha21")
    if not (0.0 <= alpha12 <= 1.0 and 0.0 <= alpha21 <= 1.0):
        raise ContractError("parámetros: alpha12 y alpha21 deben estar en [0, 1]")

    source_id = str(row["source_id"]).strip()
    if not source_id:
        raise ContractError("parámetros: source_id no puede estar vacío")
    return NrtlParameters(
        source_id=source_id,
        component_1=component_1,
        component_2=component_2,
        convention=canonical_convention,
        a12=_finite_number(row["A12"], "A12"),
        a21=_finite_number(row["A21"], "A21"),
        b12=_finite_number(row["B12"], "B12"),
        b21=_finite_number(row["B21"], "B21"),
        alpha12=alpha12,
        alpha21=alpha21,
    )


def read_dwsim_points(path: Path, parameters: NrtlParameters) -> pd.DataFrame:
    if not path.is_file():
        raise ContractError(f"no existe el CSV de puntos DWSIM: {path}")
    try:
        frame = pd.read_csv(path)
    except (OSError, pd.errors.ParserError) as exc:
        raise ContractError(f"no se pudo leer el CSV de puntos DWSIM: {exc}") from exc
    required = {
        "component_1",
        "component_2",
        "temperature_K",
        "x_component_1",
        "gamma_component_1_dwsim",
        "gamma_component_2_dwsim",
    }
    _require_columns(frame, required, "puntos DWSIM")
    if frame.empty:
        raise ContractError("puntos DWSIM: el CSV no contiene observaciones")
    if frame[list(required)].isna().any().any():
        raise ContractError("puntos DWSIM: hay valores obligatorios vacíos")

    c1 = frame["component_1"].astype(str).map(_normalise)
    c2 = frame["component_2"].astype(str).map(_normalise)
    if not (c1 == _normalise(parameters.component_1)).all() or not (
        c2 == _normalise(parameters.component_2)
    ).all():
        raise ContractError(
            "puntos DWSIM: el orden de componentes no coincide con el contrato de parámetros"
        )

    numeric_columns = [
        "temperature_K",
        "x_component_1",
        "gamma_component_1_dwsim",
        "gamma_component_2_dwsim",
    ]
    numeric = frame[numeric_columns].apply(pd.to_numeric, errors="coerce")
    if not np.isfinite(numeric.to_numpy(dtype=float)).all():
        raise ContractError("puntos DWSIM: todos los valores numéricos deben ser finitos")
    frame = frame.copy()
    frame[numeric_columns] = numeric
    if (frame["temperature_K"] <= 0.0).any():
        raise ContractError("puntos DWSIM: temperature_K debe ser positiva")
    if not frame["x_component_1"].between(0.0, 1.0).all():
        raise ContractError("puntos DWSIM: x_component_1 debe estar en [0, 1]")
    if (frame[["gamma_component_1_dwsim", "gamma_component_2_dwsim"]] <= 0.0).any().any():
        raise ContractError("puntos DWSIM: los coeficientes de actividad deben ser positivos")
    if "x_component_2" in frame.columns:
        x2 = pd.to_numeric(frame["x_component_2"], errors="coerce")
        if not np.isfinite(x2.to_numpy(dtype=float)).all():
            raise ContractError("puntos DWSIM: x_component_2 debe ser finito")
        if not np.allclose(frame["x_component_1"] + x2, 1.0, rtol=0.0, atol=1.0e-8):
            raise ContractError("puntos DWSIM: x_component_1 + x_component_2 debe ser 1")
    return frame


def calculate_nrtl(
    temperatures_k: np.ndarray,
    x1: np.ndarray,
    parameters: NrtlParameters,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Calcula gamma1 y gamma2 para una mezcla binaria NRTL."""
    if parameters.convention == "tau_ij=A_ij+B_ij/T_K":
        tau12 = parameters.a12 + parameters.b12 / temperatures_k
        tau21 = parameters.a21 + parameters.b21 / temperatures_k
    else:
        tau12 = (parameters.a12 + parameters.b12 * temperatures_k) / (
            R_J_MOL_K * temperatures_k
        )
        tau21 = (parameters.a21 + parameters.b21 * temperatures_k) / (
            R_J_MOL_K * temperatures_k
        )

    x2 = 1.0 - x1
    with np.errstate(over="raise", invalid="raise", divide="raise"):
        g12 = np.exp(-parameters.alpha12 * tau12)
        g21 = np.exp(-parameters.alpha21 * tau21)
        denominator_21 = x1 + x2 * g21
        denominator_12 = x2 + x1 * g12
        ln_gamma1 = x2**2 * (
            tau21 * (g21 / denominator_21) ** 2
            + tau12 * g12 / denominator_12**2
        )
        ln_gamma2 = x1**2 * (
            tau12 * (g12 / denominator_12) ** 2
            + tau21 * g21 / denominator_21**2
        )
        gamma1 = np.exp(ln_gamma1)
        gamma2 = np.exp(ln_gamma2)
    values = np.column_stack((tau12, tau21, gamma1, gamma2))
    if not np.isfinite(values).all() or (gamma1 <= 0.0).any() or (gamma2 <= 0.0).any():
        raise ContractError("el cálculo NRTL produjo valores no finitos o no positivos")
    return tau12, tau21, gamma1, gamma2


def build_comparison(
    points: pd.DataFrame,
    parameters: NrtlParameters,
    tolerance_percent: float,
) -> pd.DataFrame:
    temperatures = points["temperature_K"].to_numpy(dtype=float)
    x1 = points["x_component_1"].to_numpy(dtype=float)
    tau12, tau21, gamma1, gamma2 = calculate_nrtl(temperatures, x1, parameters)
    gamma1_ref = points["gamma_component_1_dwsim"].to_numpy(dtype=float)
    gamma2_ref = points["gamma_component_2_dwsim"].to_numpy(dtype=float)
    error1 = np.abs(gamma1 - gamma1_ref) / gamma1_ref * 100.0
    error2 = np.abs(gamma2 - gamma2_ref) / gamma2_ref * 100.0
    maximum = np.maximum(error1, error2)
    return pd.DataFrame(
        {
            "source_id": parameters.source_id,
            "component_1": parameters.component_1,
            "component_2": parameters.component_2,
            "convention": parameters.convention,
            "temperature_K": temperatures,
            "x_component_1": x1,
            "x_component_2": 1.0 - x1,
            "tau_12": tau12,
            "tau_21": tau21,
            "gamma_component_1_calculated": gamma1,
            "gamma_component_1_dwsim": gamma1_ref,
            "relative_error_component_1_percent": error1,
            "gamma_component_2_calculated": gamma2,
            "gamma_component_2_dwsim": gamma2_ref,
            "relative_error_component_2_percent": error2,
            "max_relative_error_percent": maximum,
            "tolerance_percent": tolerance_percent,
            "status": np.where(maximum <= tolerance_percent, "PASS", "FAIL"),
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
    parameters: Path,
    dwsim_points: Path,
    output: Path,
) -> tuple[Path, Path, Path]:
    resolved = (
        parameters.expanduser().resolve(),
        dwsim_points.expanduser().resolve(),
        output.expanduser().resolve(),
    )
    labels = ("--parameters", "--dwsim-points", "--output")
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
    parser.add_argument("--parameters", type=Path, default=DEFAULT_PARAMETERS)
    parser.add_argument("--dwsim-points", type=Path, default=DEFAULT_DWSIM_POINTS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--tolerance-percent", type=float, default=0.5)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not math.isfinite(args.tolerance_percent) or args.tolerance_percent < 0.0:
        _emit(
            "NOT_RUN",
            "La tolerancia debe ser finita y no negativa.",
            output_written=False,
        )
        return 2
    try:
        parameters_path, dwsim_points_path, output_path = _resolve_contract_paths(
            args.parameters,
            args.dwsim_points,
            args.output,
        )
        parameters = read_parameter_contract(parameters_path)
        points = read_dwsim_points(dwsim_points_path, parameters)
        comparison = build_comparison(points, parameters, args.tolerance_percent)
    except (ContractError, FloatingPointError) as exc:
        _emit(
            "NOT_RUN",
            str(exc),
            parameters_csv=str(args.parameters.expanduser().resolve()),
            dwsim_points_csv=str(args.dwsim_points.expanduser().resolve()),
            output_csv=str(args.output.expanduser().resolve()),
            output_written=False,
        )
        return 2

    overall = "PASS" if (comparison["status"] == "PASS").all() else "FAIL"
    _write_csv_atomic(comparison, output_path)
    _emit(
        overall,
        "Contraste NRTL ejecutado con contrato completo.",
        rows=int(len(comparison)),
        max_relative_error_percent=float(comparison["max_relative_error_percent"].max()),
        tolerance_percent=float(args.tolerance_percent),
        output_csv=str(output_path),
        output_written=True,
    )
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
