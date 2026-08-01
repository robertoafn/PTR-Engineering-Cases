"""Motor declarativo de validación cuantitativa para casos PTR.

El motor lee ``validation_spec.yaml`` y no contiene condicionales por número de
caso. Por omisión trabaja exclusivamente con datasets versionados. La ejecución
DWSIM es opcional y se realiza en un proceso separado, siempre sobre una copia
temporal de la simulación.

Uso:
    python scripts/validate_case.py cases/001_slug --source dataset
    python scripts/validate_case.py cases/ --source auto
    python scripts/validate_case.py cases/001_slug --write-artifacts
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import io
import json
import math
import operator
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable, Iterable, Mapping
from pathlib import Path
from typing import Any

import pandas as pd
import yaml
from jsonschema import Draft202012Validator

try:
    from scripts import (
        compute_checksums,
        unit_consistency_check,
        validate_metadata,
        validate_tables,
    )
except ImportError:  # Ejecución directa: ``python scripts/validate_case.py``.
    import compute_checksums  # type: ignore[no-redef]
    import unit_consistency_check  # type: ignore[no-redef]
    import validate_metadata  # type: ignore[no-redef]
    import validate_tables  # type: ignore[no-redef]

ROOT = Path(__file__).resolve().parents[1]
SPEC_SCHEMA = ROOT / "schemas" / "validation_spec.schema.json"
RESULT_SCHEMA = ROOT / "schemas" / "validation_result.schema.json"
DEFAULT_RUNNER = (
    ROOT
    / "tools"
    / "dwsim_automation_runner"
    / "bin"
    / "DwsimValidationRunner.exe"
)
AUTO_START = "<!-- PTR-VALIDATION:AUTO:START -->"
AUTO_END = "<!-- PTR-VALIDATION:AUTO:END -->"
PARTIAL_STATUSES = {"N_A", "NOT_RUN", "NOT_DEMONSTRATED"}
STATUS_LABEL = {
    "PASS": "✅ PASS",
    "FAIL": "❌ FAIL",
    "N_A": "➖ N/A",
    "NOT_RUN": "⏸ NOT_RUN",
    "NOT_DEMONSTRATED": "⚠️ NOT_DEMONSTRATED",
}
COMPARATORS: dict[str, Callable[[float, float], bool]] = {
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
    "==": operator.eq,
    "!=": operator.ne,
}


class ValidationConfigurationError(ValueError):
    """La especificación o una ruta declarada es inválida."""


class EvidenceUnavailable(RuntimeError):
    """La evidencia requerida no existe en la fuente seleccionada."""


def _relative(path: Path, base: Path = ROOT) -> str:
    try:
        return path.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def _safe_case_path(case_dir: Path, relative_path: str) -> Path:
    candidate = (case_dir / relative_path).resolve()
    try:
        candidate.relative_to(case_dir.resolve())
    except ValueError as exc:
        raise ValidationConfigurationError(
            f"ruta fuera del caso: {relative_path}"
        ) from exc
    return candidate


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_case_dirs(target: Path) -> Iterable[Path]:
    """Descubre casos sin mantener una lista codificada."""
    target = target.resolve()
    if (target / "metadata.yaml").is_file():
        yield target
        return
    if not target.is_dir():
        return
    for metadata in sorted(target.glob("[0-9][0-9][0-9]_*/metadata.yaml")):
        if metadata.parent.name.startswith("000_"):
            continue
        yield metadata.parent


def load_spec(case_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    metadata_path = case_dir / "metadata.yaml"
    spec_path = case_dir / "validation_spec.yaml"
    if not metadata_path.is_file():
        raise ValidationConfigurationError(f"falta {metadata_path}")
    if not spec_path.is_file():
        raise ValidationConfigurationError(f"falta {spec_path}")
    try:
        metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8")) or {}
        spec = yaml.safe_load(spec_path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        raise ValidationConfigurationError(f"YAML no legible: {exc}") from exc

    schema = json.loads(SPEC_SCHEMA.read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema).iter_errors(spec),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        detail = "; ".join(
            f"{'/'.join(map(str, error.absolute_path)) or '<raíz>'}: {error.message}"
            for error in errors
        )
        raise ValidationConfigurationError(
            f"{_relative(spec_path)} no cumple el schema: {detail}"
        )
    if spec["case_id"] != metadata.get("case_id"):
        raise ValidationConfigurationError(
            "case_id de validation_spec.yaml no coincide con metadata.yaml"
        )
    criterion_ids = [criterion["id"] for criterion in spec["criteria"]]
    if len(criterion_ids) != len(set(criterion_ids)):
        raise ValidationConfigurationError("los id de criterios deben ser únicos")
    return spec, metadata


def load_datasets(
    case_dir: Path, spec: Mapping[str, Any]
) -> tuple[dict[str, pd.DataFrame], dict[str, Path]]:
    frames: dict[str, pd.DataFrame] = {}
    paths: dict[str, Path] = {}
    for alias, definition in spec["datasets"].items():
        path = _safe_case_path(case_dir, definition["path"])
        if not path.is_file():
            raise EvidenceUnavailable(f"dataset ausente: {definition['path']}")
        try:
            frames[alias] = pd.read_csv(path)
        except (OSError, pd.errors.ParserError) as exc:
            raise EvidenceUnavailable(
                f"dataset no legible: {definition['path']}: {exc}"
            ) from exc
        paths[alias] = path
    return frames, paths


def _normalise_runner_objects(payload: Mapping[str, Any]) -> pd.DataFrame:
    aliases = {
        "temperature_k": "temperature_K",
        "pressure_pa": "pressure_Pa",
        "specific_enthalpy_kj_kg": "specific_enthalpy_kJ_kg",
        "energy_flow_kw": "energy_flow_kW",
        "duty_kw": "duty_kW",
    }
    rows: list[dict[str, Any]] = []
    for item in payload.get("objects", []) or []:
        row: dict[str, Any] = {
            # DWSIM usa GUID internos; los manifiestos versionan tags legibles.
            "object_id": (
                item.get("object_tag")
                or item.get("tag")
                or item.get("id")
                or item.get("object_id")
            ),
            "object_type": item.get("type") or item.get("object_type"),
        }
        properties = item.get("properties") or {}
        for key, value in properties.items():
            row[aliases.get(key, key)] = value
        for key, value in item.items():
            if key not in {"id", "type", "properties", "warnings"}:
                row.setdefault(aliases.get(key, key), value)
        if row.get("energy_flow_kW") is None and row.get("duty_kW") is not None:
            row["energy_flow_kW"] = row["duty_kW"]
        if isinstance(row["object_id"], str):
            row["object_id"] = row["object_id"].strip()
        rows.append(row)
    return pd.DataFrame(rows)


def _merge_dwsim_evidence(
    frames: dict[str, pd.DataFrame],
    spec: Mapping[str, Any],
    payload: Mapping[str, Any],
) -> None:
    api = _normalise_runner_objects(payload)
    if api.empty or "object_id" not in api:
        raise EvidenceUnavailable("DWSIM no devolvió objetos utilizables")
    object_map = (spec.get("dwsim") or {}).get("object_map") or {}
    reverse_map = {dwsim_id: canonical for canonical, dwsim_id in object_map.items()}
    api["object_id"] = api["object_id"].replace(reverse_map)
    referenced_by_dataset = _referenced_ids_by_dataset(spec)
    dataset_ids: set[str] = set()
    for alias, frame in frames.items():
        id_column = spec["datasets"][alias].get("id_column", "object_id")
        if id_column in frame:
            dataset_ids.update(frame[id_column].dropna().astype(str))
    api_ids = set(api["object_id"].dropna().astype(str))
    explicitly_requested = (
        set().union(*referenced_by_dataset.values())
        if referenced_by_dataset
        else set()
    )
    if not dataset_ids.intersection(api_ids) and not explicitly_requested.intersection(api_ids):
        raise EvidenceUnavailable(
            "los identificadores devueltos por DWSIM no se pueden mapear a los datasets"
        )
    for alias, frame in frames.items():
        id_column = spec["datasets"][alias].get("id_column", "object_id")
        if id_column not in frame.columns:
            continue
        frame_ids = set(frame[id_column].dropna().astype(str))
        allowed_api_ids = frame_ids | referenced_by_dataset.get(alias, set())
        api_for_frame = api[
            api["object_id"].astype(str).isin(allowed_api_ids)
        ].rename(columns={"object_id": id_column})
        if api_for_frame.empty:
            continue
        merged = frame.merge(
            api_for_frame,
            on=id_column,
            how="outer",
            suffixes=("_dataset", ""),
        )
        for column in frame.columns:
            dataset_column = f"{column}_dataset"
            if dataset_column not in merged:
                continue
            if column in merged:
                merged[column] = merged[column].combine_first(merged[dataset_column])
            else:
                merged.rename(columns={dataset_column: column}, inplace=True)
        frames[alias] = merged


def _referenced_ids_by_dataset(
    spec: Mapping[str, Any],
) -> dict[str, set[str]]:
    """Relaciona IDs con el alias donde un criterio los usa explícitamente."""
    referenced: dict[str, set[str]] = {}

    def add(selector: Any) -> None:
        if not isinstance(selector, Mapping) or "dataset" not in selector:
            return
        referenced.setdefault(str(selector["dataset"]), set()).update(
            str(item) for item in selector.get("ids") or []
        )

    for criterion in spec.get("criteria", []):
        alias = criterion.get("dataset")
        if alias:
            ids = [
                *(criterion.get("ids") or []),
                *(criterion.get("inlet_ids") or []),
                *(criterion.get("outlet_ids") or []),
            ]
            referenced.setdefault(str(alias), set()).update(str(item) for item in ids)
        for key in ("left", "right", "value", "normalization_reference"):
            add(criterion.get(key))
        for term in criterion.get("terms") or []:
            add(term)
    return referenced


def _collect_object_ids(spec: Mapping[str, Any]) -> list[str]:
    object_ids: set[str] = set()
    for criterion in spec["criteria"]:
        object_ids.update(criterion.get("ids") or [])
        for key in ("inlet_ids", "outlet_ids"):
            object_ids.update(criterion.get(key) or [])
        for key in ("left", "right", "value", "normalization_reference"):
            operand = criterion.get(key)
            if isinstance(operand, dict):
                object_ids.update(operand.get("ids") or [])
        for term in criterion.get("terms") or []:
            object_ids.update(term.get("ids") or [])
    object_map = (spec.get("dwsim") or {}).get("object_map") or {}
    return sorted(object_map.get(item, item) for item in object_ids)


def run_dwsim(
    case_dir: Path,
    spec: Mapping[str, Any],
    *,
    dwsim_home: Path | None,
    runner_path: Path = DEFAULT_RUNNER,
) -> tuple[dict[str, Any], str]:
    dwsim = spec.get("dwsim")
    if not dwsim:
        raise EvidenceUnavailable("validation_spec.yaml no declara una simulación DWSIM")
    if not runner_path.is_file():
        raise EvidenceUnavailable(f"runner DWSIM no disponible: {_relative(runner_path)}")
    simulation = _safe_case_path(case_dir, dwsim["file"])
    if not simulation.is_file():
        raise EvidenceUnavailable(f"simulación ausente: {dwsim['file']}")

    original_hash = sha256(simulation)
    with tempfile.TemporaryDirectory(prefix="ptr_dwsim_") as temporary:
        temporary_simulation = Path(temporary) / simulation.name
        shutil.copy2(simulation, temporary_simulation)
        command = [
            str(runner_path),
            "--simulation",
            str(temporary_simulation),
            "--required-version",
            str(dwsim["required_version"]),
        ]
        object_ids = _collect_object_ids(spec)
        if object_ids:
            command.extend(["--objects", ",".join(object_ids)])
        if dwsim_home:
            command.extend(["--dwsim-home", str(dwsim_home)])
        try:
            completed = subprocess.run(
                command,
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
                timeout=int(dwsim.get("timeout_seconds", 120)),
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise EvidenceUnavailable(f"no fue posible ejecutar DWSIM: {exc}") from exc
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            stderr = completed.stderr.strip()
            detail = f"; stderr: {stderr}" if stderr else ""
            raise EvidenceUnavailable(
                f"runner DWSIM no emitió JSON válido{detail}"
            ) from exc
        if completed.returncode != 0 or not payload.get("solved", False):
            errors = payload.get("errors") or []
            raise EvidenceUnavailable(
                "DWSIM no resolvió el caso: "
                + (json.dumps(errors, ensure_ascii=False) if errors else "error desconocido")
            )
        if not payload.get("version_compatible", True):
            raise EvidenceUnavailable(
                "versión DWSIM incompatible: "
                f"{payload.get('dwsim_version')} (requerida {dwsim['required_version']})"
            )
        if sha256(temporary_simulation) != original_hash:
            raise EvidenceUnavailable("el runner modificó la copia de la simulación")
    if sha256(simulation) != original_hash:
        raise RuntimeError("la simulación original cambió durante la validación")
    return payload, str(payload.get("dwsim_version") or "")


def _dataset_for_selector(
    selector: Mapping[str, Any],
    frames: Mapping[str, pd.DataFrame],
) -> pd.DataFrame:
    alias = selector["dataset"]
    if alias not in frames:
        raise EvidenceUnavailable(f"dataset no declarado: {alias}")
    return frames[alias]


def _selector_value(
    selector: Mapping[str, Any],
    frames: Mapping[str, pd.DataFrame],
    spec: Mapping[str, Any],
) -> float:
    frame = _dataset_for_selector(selector, frames)
    column = selector["column"]
    if column not in frame.columns:
        raise EvidenceUnavailable(
            f"columna ausente: {selector['dataset']}.{column}"
        )
    selected = frame
    ids = selector.get("ids")
    if ids:
        id_column = spec["datasets"][selector["dataset"]].get(
            "id_column", "object_id"
        )
        if id_column not in selected.columns:
            raise EvidenceUnavailable(
                f"columna identificadora ausente: {selector['dataset']}.{id_column}"
            )
        selected = selected[selected[id_column].isin(ids)]
        missing_ids = sorted(set(ids) - set(selected[id_column].astype(str)))
        if missing_ids:
            raise EvidenceUnavailable(
                f"objetos ausentes en {selector['dataset']}: {', '.join(missing_ids)}"
            )
    for where_column, expected in (selector.get("where") or {}).items():
        if where_column not in selected.columns:
            raise EvidenceUnavailable(
                f"columna de filtro ausente: {selector['dataset']}.{where_column}"
            )
        selected = selected[selected[where_column] == expected]
    if selected.empty:
        raise EvidenceUnavailable(f"selector sin filas en {selector['dataset']}")

    aggregate = selector.get("aggregate", "first")
    series = selected[column]
    if aggregate == "count":
        value = float(series.count())
    else:
        numeric = pd.to_numeric(series, errors="coerce").dropna()
        if numeric.empty:
            raise EvidenceUnavailable(
                f"sin valores numéricos en {selector['dataset']}.{column}"
            )
        if aggregate == "first":
            if len(numeric) != 1:
                raise ValidationConfigurationError(
                    f"selector ambiguo ({len(numeric)} filas); declare aggregate"
                )
            value = float(numeric.iloc[0])
        else:
            value = float(getattr(numeric, aggregate)())
    value *= float(selector.get("factor", 1.0))
    return abs(value) if selector.get("absolute", False) else value


def _metadata_output(metadata: Mapping[str, Any], name: str) -> float:
    matches = [item for item in metadata.get("outputs", []) if item.get("name") == name]
    if len(matches) != 1:
        raise EvidenceUnavailable(f"output de metadata no disponible o ambiguo: {name}")
    try:
        return float(matches[0]["value"])
    except (KeyError, TypeError, ValueError) as exc:
        raise EvidenceUnavailable(f"output no numérico en metadata: {name}") from exc


def _operand_value(
    operand: Any,
    frames: Mapping[str, pd.DataFrame],
    spec: Mapping[str, Any],
    metadata: Mapping[str, Any],
) -> tuple[float, str]:
    if isinstance(operand, int | float) and not isinstance(operand, bool):
        return float(operand), "reported_metric"
    if not isinstance(operand, Mapping):
        raise ValidationConfigurationError("operando inválido")
    if "metadata_output" in operand:
        value = _metadata_output(metadata, operand["metadata_output"])
        value *= float(operand.get("factor", 1.0))
        if operand.get("absolute", False):
            value = abs(value)
        return value, "reported_metric"
    return _selector_value(operand, frames, spec), "exported_dataset"


def _threshold_passes(value: float, threshold: Mapping[str, Any]) -> bool:
    return COMPARATORS[threshold["operator"]](value, float(threshold["value"]))


def _base_result(criterion: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": criterion["id"],
        "title": criterion["title"],
        "type": criterion["type"],
        "scope": criterion["scope"],
        "blocking": criterion["blocking"],
        "required": criterion["required"],
        "status": "NOT_RUN",
        "evidence_source": "not_available",
        "result": None,
        "threshold": criterion.get("threshold"),
        "message": "",
        "evidence_paths": list(criterion.get("evidence_paths") or []),
    }


def _set_numeric_result(
    result: dict[str, Any],
    criterion: Mapping[str, Any],
    value: float,
    *,
    unit: str,
    evidence_source: str,
    condition: bool | None = None,
    message: str = "",
) -> dict[str, Any]:
    if not math.isfinite(value):
        raise EvidenceUnavailable("el cálculo produjo un valor no finito")
    threshold = criterion.get("threshold")
    passes = condition if condition is not None else (
        _threshold_passes(value, threshold) if threshold else True
    )
    result.update(
        {
            "status": "PASS" if passes else criterion.get("failure_status", "FAIL"),
            "evidence_source": evidence_source,
            "result": {"value": value, "unit": unit},
            "message": message or ("criterio cumplido" if passes else "criterio no cumplido"),
        }
    )
    return result


def _mass_balance(
    criterion: Mapping[str, Any],
    frames: Mapping[str, pd.DataFrame],
    spec: Mapping[str, Any],
) -> tuple[float, str]:
    alias = criterion["dataset"]
    value_column = criterion.get("value_column", "mass_flow_kg_s")
    common = {"dataset": alias, "column": value_column, "aggregate": "sum"}
    inlet = _selector_value({**common, "ids": criterion["inlet_ids"]}, frames, spec)
    outlet = _selector_value({**common, "ids": criterion["outlet_ids"]}, frames, spec)
    denominator = max(abs(inlet), sys.float_info.epsilon)
    return abs(inlet - outlet) / denominator * 100.0, (
        f"entrada={inlet:.12g}; salida={outlet:.12g}"
    )


def _energy_balance(
    criterion: Mapping[str, Any],
    frames: Mapping[str, pd.DataFrame],
    spec: Mapping[str, Any],
    metadata: Mapping[str, Any],
) -> tuple[float, str]:
    if criterion.get("terms"):
        values = [_selector_value(term, frames, spec) for term in criterion["terms"]]
        residual = abs(sum(values))
        normalization = criterion.get("normalization", "sum_absolute_terms")
        if normalization == "sum_absolute_terms":
            denominator = sum(abs(value) for value in values)
        elif normalization == "reference":
            reference, _ = _operand_value(
                criterion.get("normalization_reference"),
                frames,
                spec,
                metadata,
            )
            denominator = abs(reference)
        else:
            positives = sum(value for value in values if value > 0)
            negatives = abs(sum(value for value in values if value < 0))
            denominator = {
                "inlet_sum": positives,
                "outlet_sum": negatives,
                "max_side": max(positives, negatives),
            }[normalization]
        if denominator <= sys.float_info.epsilon:
            raise EvidenceUnavailable("normalización energética nula")
        return residual / denominator * 100.0, f"residuo={residual:.12g}"

    alias = criterion["dataset"]
    value_column = criterion.get("value_column", "energy_flow_kW")
    common = {"dataset": alias, "column": value_column, "aggregate": "sum"}
    inlet = _selector_value({**common, "ids": criterion["inlet_ids"]}, frames, spec)
    outlet = _selector_value({**common, "ids": criterion["outlet_ids"]}, frames, spec)
    denominator = max(abs(inlet), abs(outlet), sys.float_info.epsilon)
    return abs(inlet - outlet) / denominator * 100.0, (
        f"entrada={inlet:.12g}; salida={outlet:.12g}"
    )


def _run_existing_validators(
    case_dir: Path, validators: list[str]
) -> tuple[int, str]:
    results: list[tuple[str, int, str]] = []
    for name in validators:
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            if name == "metadata":
                with tempfile.TemporaryDirectory(prefix="ptr_metadata_reports_") as temp:
                    original_reports = validate_metadata.REPORTS
                    try:
                        validate_metadata.REPORTS = Path(temp)
                        code = validate_metadata.validate(case_dir)
                    finally:
                        validate_metadata.REPORTS = original_reports
            elif name == "tables":
                code = validate_tables.main(case_dir)
            elif name == "units":
                code = unit_consistency_check.main(case_dir)
            elif name == "checksums":
                code = compute_checksums.process_case(case_dir, verify=True)
            else:  # Protegido adicionalmente por JSON Schema.
                raise ValidationConfigurationError(f"validador desconocido: {name}")
        results.append((name, int(code), captured.getvalue().strip()))
    errors = sum(code != 0 for _, code, _ in results)
    detail = " | ".join(
        f"{name}: {'OK' if code == 0 else 'FAIL'}"
        + (f" ({output})" if output else "")
        for name, code, output in results
    )
    return errors, detail


def _api_dataset_consistency(
    criterion: Mapping[str, Any],
    frames: Mapping[str, pd.DataFrame],
    spec: Mapping[str, Any],
) -> tuple[float, str]:
    alias = criterion["dataset"]
    if alias not in frames:
        raise EvidenceUnavailable(f"dataset no declarado: {alias}")
    frame = frames[alias]
    id_column = spec["datasets"][alias].get("id_column", "object_id")
    if id_column not in frame:
        raise EvidenceUnavailable(f"columna identificadora ausente: {alias}.{id_column}")
    selected = frame
    ids = criterion.get("ids") or []
    if ids:
        selected = selected[selected[id_column].isin(ids)]
        missing = sorted(set(ids) - set(selected[id_column].astype(str)))
        if missing:
            raise EvidenceUnavailable(
                f"objetos ausentes para comparación API: {', '.join(missing)}"
            )
    if selected.empty:
        raise EvidenceUnavailable("sin filas para comparar API y dataset")

    differences: list[tuple[float, str, str, float, float]] = []
    for columns in criterion.get("columns") or []:
        dataset_name = columns["dataset_column"]
        api_name = columns["api_column"]
        preserved_name = f"{dataset_name}_dataset"
        if preserved_name in selected:
            dataset_series = selected[preserved_name]
        elif dataset_name != api_name and dataset_name in selected:
            dataset_series = selected[dataset_name]
        else:
            raise EvidenceUnavailable(
                f"evidencia original no preservada: {alias}.{dataset_name}"
            )
        if api_name not in selected:
            raise EvidenceUnavailable(f"columna API ausente: {alias}.{api_name}")
        dataset_values = pd.to_numeric(dataset_series, errors="coerce")
        api_values = pd.to_numeric(selected[api_name], errors="coerce")
        valid = dataset_values.notna() & api_values.notna()
        if not valid.any():
            raise EvidenceUnavailable(
                f"sin pares comparables: {dataset_name} ↔ {api_name}"
            )
        dataset_factor = float(columns.get("dataset_factor", 1.0))
        api_factor = float(columns.get("api_factor", 1.0))
        for index in selected.index[valid]:
            dataset_value = float(dataset_values.loc[index]) * dataset_factor
            api_value = float(api_values.loc[index]) * api_factor
            denominator = max(abs(dataset_value), sys.float_info.epsilon)
            difference = abs(api_value - dataset_value) / denominator * 100.0
            differences.append(
                (
                    difference,
                    str(selected.loc[index, id_column]),
                    f"{dataset_name}↔{api_name}",
                    dataset_value,
                    api_value,
                )
            )
    if not differences:
        raise ValidationConfigurationError("columns no puede estar vacío")
    worst = max(differences, key=lambda item: item[0])
    return worst[0], (
        f"máxima discrepancia en {worst[1]} {worst[2]}: "
        f"dataset={worst[3]:.12g}; api={worst[4]:.12g}"
    )


def evaluate_criterion(
    criterion: Mapping[str, Any],
    *,
    case_dir: Path,
    frames: Mapping[str, pd.DataFrame],
    spec: Mapping[str, Any],
    metadata: Mapping[str, Any],
    actual_source: str,
) -> dict[str, Any]:
    result = _base_result(criterion)
    criterion_type = criterion["type"]
    source = "dwsim_api" if actual_source == "dwsim_api" else "exported_dataset"
    try:
        if criterion_type == "api_dataset_consistency":
            if actual_source != "dwsim_api":
                raise EvidenceUnavailable(
                    "la comparación API↔dataset requiere una ejecución DWSIM"
                )
            value, detail = _api_dataset_consistency(criterion, frames, spec)
            return _set_numeric_result(
                result,
                criterion,
                value,
                unit="%",
                evidence_source="dwsim_api",
                message=detail,
            )
        if criterion_type in {"global_mass_balance", "side_mass_balance"}:
            value, detail = _mass_balance(criterion, frames, spec)
            return _set_numeric_result(
                result, criterion, value, unit="%", evidence_source=source, message=detail
            )
        if criterion_type == "stream_energy_balance":
            value, detail = _energy_balance(criterion, frames, spec, metadata)
            return _set_numeric_result(
                result, criterion, value, unit="%", evidence_source=source, message=detail
            )
        if criterion_type == "existing_validators":
            validators = list(criterion.get("validators") or [])
            if not validators:
                raise ValidationConfigurationError("validators no puede estar vacío")
            errors, detail = _run_existing_validators(case_dir, validators)
            return _set_numeric_result(
                result,
                criterion,
                float(errors),
                unit="errores",
                evidence_source="existing_validator",
                condition=errors == 0,
                message=detail,
            )

        left_operand = criterion.get("left", criterion.get("value"))
        if left_operand is None:
            if criterion.get("dataset") and criterion.get("value_column"):
                left_operand = {
                    "dataset": criterion["dataset"],
                    "column": criterion["value_column"],
                    "ids": criterion.get("inlet_ids") or criterion.get("outlet_ids"),
                    "aggregate": "first",
                }
            else:
                raise ValidationConfigurationError("falta value o left")
        left, left_source = _operand_value(left_operand, frames, spec, metadata)

        if criterion_type == "range":
            minimum = criterion.get("minimum", -math.inf)
            maximum = criterion.get("maximum", math.inf)
            condition = float(minimum) <= left <= float(maximum)
            unit = (criterion.get("threshold") or {}).get("unit", "dimensionless")
            return _set_numeric_result(
                result,
                criterion,
                left,
                unit=unit,
                evidence_source=left_source if actual_source != "dwsim_api" else source,
                condition=condition,
                message=f"rango=[{minimum}, {maximum}]",
            )

        if criterion_type == "reported_metric":
            unit = (criterion.get("threshold") or {}).get("unit", "dimensionless")
            return _set_numeric_result(
                result,
                criterion,
                left,
                unit=unit,
                evidence_source=left_source,
            )

        right_operand = criterion.get("right")
        if criterion_type == "pressure_margin" and right_operand is None:
            unit = (criterion.get("threshold") or {}).get("unit", "Pa")
            return _set_numeric_result(
                result,
                criterion,
                left,
                unit=unit,
                evidence_source=(
                    "dwsim_api" if actual_source == "dwsim_api" else left_source
                ),
            )
        if right_operand is None:
            raise ValidationConfigurationError("falta right")
        right, right_source = _operand_value(right_operand, frames, spec, metadata)
        calculation = criterion.get("calculation")
        if criterion_type == "isenthalpic" and not calculation:
            calculation = "relative_difference_percent"
        elif criterion_type == "pressure_margin" and not calculation:
            calculation = "absolute_difference"
        elif not calculation:
            calculation = "relative_difference_percent"

        if calculation == "value":
            value = left
        elif calculation == "absolute_difference":
            value = left - right if criterion_type == "pressure_margin" else abs(left - right)
        elif calculation == "relative_difference_percent":
            value = abs(left - right) / max(abs(left), sys.float_info.epsilon) * 100.0
        elif calculation == "ratio":
            if abs(right) <= sys.float_info.epsilon:
                raise EvidenceUnavailable("división por cero en ratio")
            value = left / right
        else:
            raise ValidationConfigurationError(f"calculation desconocido: {calculation}")
        unit = (criterion.get("threshold") or {}).get("unit", "dimensionless")
        evidence_source = (
            "dwsim_api"
            if actual_source == "dwsim_api"
            else (
                "reported_metric"
                if left_source == right_source == "reported_metric"
                else "exported_dataset"
            )
        )
        return _set_numeric_result(
            result,
            criterion,
            value,
            unit=unit,
            evidence_source=evidence_source,
            message=f"izquierda={left:.12g}; derecha={right:.12g}",
        )
    except EvidenceUnavailable as exc:
        result.update(
            {
                "status": criterion.get("unavailable_status", "N_A"),
                "evidence_source": "not_available",
                "message": str(exc),
            }
        )
        return result
    except (KeyError, TypeError, ValueError) as exc:
        raise ValidationConfigurationError(
            f"criterio {criterion['id']}: {exc}"
        ) from exc


def _scope_status(criteria: list[dict[str, Any]]) -> str:
    if not criteria:
        return "NOT_RUN"
    if any(item["status"] == "FAIL" for item in criteria):
        return "FAIL"
    if any(item["status"] in PARTIAL_STATUSES for item in criteria):
        return "CONDITIONAL"
    return "PASS"


def _overall_status(criteria: list[dict[str, Any]]) -> str:
    if any(item["status"] == "FAIL" and item["blocking"] for item in criteria):
        return "FAIL"
    if any(
        item["status"] == "FAIL"
        or (item["required"] and item["status"] in PARTIAL_STATUSES)
        for item in criteria
    ):
        return "CONDITIONAL"
    return "PASS"


def _discover_figures(case_dir: Path) -> list[str]:
    figures_dir = case_dir / "assets" / "figures"
    if not figures_dir.is_dir():
        return []
    allowed = {".png", ".jpg", ".jpeg", ".svg", ".webp"}
    return [
        _relative(path)
        for path in sorted(figures_dir.rglob("*"))
        if path.is_file() and path.suffix.lower() in allowed
    ]


def _utc_now() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _configuration_failure(
    case_dir: Path,
    *,
    source: str,
    validator: str,
    message: str,
) -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "case_id": case_dir.name,
        "case_version": "desconocida",
        "generated_at_utc": _utc_now(),
        "validator": validator,
        "requested_source": source,
        "actual_source": "not_available",
        "dwsim_version": None,
        "overall_status": "FAIL",
        "lifecycle_status": "draft",
        "source_message": message,
        "scopes": {},
        "criteria": [],
        "datasets": [],
        "figures": [],
    }


def validate_result_document(result: Mapping[str, Any]) -> None:
    """Comprueba el contrato que consumirá el futuro dashboard."""
    schema = json.loads(RESULT_SCHEMA.read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema).iter_errors(result),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        detail = "; ".join(
            f"{'/'.join(map(str, error.absolute_path)) or '<raíz>'}: {error.message}"
            for error in errors
        )
        raise ValidationConfigurationError(
            f"resultado interno no cumple validation_result.schema.json: {detail}"
        )


def validate_case(
    case_dir: Path,
    *,
    source: str = "auto",
    validator: str = "Roberto Flores Núñez",
    dwsim_home: Path | None = None,
    runner_path: Path = DEFAULT_RUNNER,
    generated_at_utc: str | None = None,
) -> dict[str, Any]:
    case_dir = case_dir.resolve()
    try:
        spec, metadata = load_spec(case_dir)
        frames, dataset_paths = load_datasets(case_dir, spec)
    except (
        ValidationConfigurationError,
        EvidenceUnavailable,
        OSError,
        json.JSONDecodeError,
    ) as exc:
        result = _configuration_failure(
            case_dir, source=source, validator=validator, message=str(exc)
        )
        validate_result_document(result)
        return result

    actual_source = "exported_dataset"
    dwsim_version: str | None = None
    source_message = "validación realizada sobre datasets exportados"
    if source in {"auto", "dwsim"}:
        try:
            payload, dwsim_version = run_dwsim(
                case_dir,
                spec,
                dwsim_home=dwsim_home,
                runner_path=runner_path,
            )
            _merge_dwsim_evidence(frames, spec, payload)
            actual_source = "dwsim_api"
            source_message = "simulación resuelta mediante DWSIM Automation API"
        except (EvidenceUnavailable, RuntimeError) as exc:
            if source == "dwsim":
                result = _configuration_failure(
                    case_dir,
                    source=source,
                    validator=validator,
                    message=str(exc),
                )
                result.update(
                    {
                        "case_id": str(metadata.get("case_id", case_dir.name)),
                        "case_version": str(metadata.get("version", "desconocida")),
                        "lifecycle_status": str(metadata.get("status", "draft")),
                        "datasets": sorted(_relative(path) for path in dataset_paths.values()),
                        "figures": _discover_figures(case_dir),
                    }
                )
                validate_result_document(result)
                return result
            source_message = f"DWSIM no disponible; fallback a datasets: {exc}"

    criteria: list[dict[str, Any]] = []
    try:
        for criterion in spec["criteria"]:
            criteria.append(
                evaluate_criterion(
                    criterion,
                    case_dir=case_dir,
                    frames=frames,
                    spec=spec,
                    metadata=metadata,
                    actual_source=actual_source,
                )
            )
    except ValidationConfigurationError as exc:
        result = _configuration_failure(
            case_dir, source=source, validator=validator, message=str(exc)
        )
        validate_result_document(result)
        return result

    scopes = {
        scope: _scope_status(
            [item for item in criteria if item["scope"] == scope]
        )
        for scope in ("numerical", "phenomenon", "safety", "data_quality")
        if any(item["scope"] == scope for item in criteria)
    }
    result = {
        "schema_version": "1.0.0",
        "case_id": str(metadata["case_id"]),
        "case_version": str(metadata["version"]),
        "generated_at_utc": generated_at_utc or _utc_now(),
        "validator": validator,
        "requested_source": source,
        "actual_source": actual_source,
        "dwsim_version": dwsim_version,
        "overall_status": _overall_status(criteria),
        "lifecycle_status": str(metadata.get("status", "draft")),
        "source_message": source_message,
        "scopes": scopes,
        "criteria": criteria,
        "datasets": sorted(_relative(path) for path in dataset_paths.values()),
        "figures": _discover_figures(case_dir),
    }
    validate_result_document(result)
    return result


def result_exit_code(result: Mapping[str, Any], *, strict: bool = False) -> int:
    if result["overall_status"] == "FAIL":
        return 1
    if strict and any(
        item["required"] and item["status"] in PARTIAL_STATUSES
        for item in result["criteria"]
    ):
        return 1
    return 0


def serialise_result(result: Mapping[str, Any]) -> str:
    """Serialización estable para artefactos, diffs y pruebas."""
    validate_result_document(result)
    return json.dumps(
        result,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
        allow_nan=False,
    ) + "\n"


def _markdown_section(result: Mapping[str, Any]) -> str:
    lines = [
        AUTO_START,
        "## Resultado automático reproducible",
        "",
        f"- **Fecha UTC:** {result['generated_at_utc']}",
        f"- **Validador:** {result['validator']}",
        f"- **Versión del caso:** {result['case_version']}",
        f"- **Fuente solicitada:** `{result['requested_source']}`",
        f"- **Fuente utilizada:** `{result['actual_source']}`",
        f"- **Resultado general:** **{result['overall_status']}**",
        f"- **Detalle de fuente:** {result['source_message']}",
        "",
        "| Criterio | Alcance | Umbral | Resultado | Estado |",
        "|---|---|---:|---:|---|",
    ]
    for criterion in result["criteria"]:
        threshold = criterion["threshold"]
        threshold_text = (
            f"{threshold['operator']} {threshold['value']} {threshold['unit']}"
            if threshold
            else "declarativo"
        )
        numeric = criterion["result"]
        result_text = (
            f"{numeric['value']:.12g} {numeric['unit']}"
            if numeric and isinstance(numeric["value"], int | float)
            else ("N/A" if numeric is None else str(numeric["value"]))
        )
        lines.append(
            f"| {criterion['title']} | {criterion['scope']} | "
            f"{threshold_text} | {result_text} | "
            f"{STATUS_LABEL[criterion['status']]} |"
        )
    lines.extend(
        [
            "",
            "### Evidencia de ejecución",
            "",
            f"- Comando base: `python scripts/validate_case.py "
            f"cases/{result['case_id']} --source {result['requested_source']}`",
            "- Resultado estructurado: `validation_results.json`",
            "",
            "Esta sección es generada por `scripts/validate_case.py`; la narrativa "
            "técnica fuera de los delimitadores se conserva.",
            AUTO_END,
        ]
    )
    return "\n".join(lines)


def write_artifacts(case_dir: Path, result: Mapping[str, Any]) -> None:
    (case_dir / "validation_results.json").write_text(
        serialise_result(result), encoding="utf-8"
    )
    report_path = case_dir / "validation_report.md"
    existing = report_path.read_text(encoding="utf-8") if report_path.is_file() else ""
    section = _markdown_section(result)
    if AUTO_START in existing and AUTO_END in existing:
        before, remainder = existing.split(AUTO_START, 1)
        _, after = remainder.split(AUTO_END, 1)
        updated = before.rstrip() + "\n\n" + section + after
    else:
        updated = existing.rstrip() + ("\n\n" if existing.strip() else "") + section + "\n"
    report_path.write_text(updated, encoding="utf-8")


def _print_results(results: list[Mapping[str, Any]]) -> None:
    print("Caso | Fuente | Resultado | Criterios")
    print("-" * 79)
    for result in results:
        summary = ", ".join(
            f"{item['id']}={item['status']}" for item in result["criteria"]
        ) or result["source_message"]
        print(
            f"{result['case_id']} | {result['actual_source']} | "
            f"{result['overall_status']} | {summary}"
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="caso o directorio cases/")
    parser.add_argument(
        "--source",
        choices=("auto", "dataset", "dwsim"),
        default="auto",
        help="fuente de evidencia solicitada",
    )
    parser.add_argument(
        "--write-artifacts",
        action="store_true",
        help="escribe validation_results.json y la sección automática Markdown",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="falla también ante criterios requeridos parciales",
    )
    parser.add_argument(
        "--validator",
        default="Roberto Flores Núñez",
        help="nombre registrado en los artefactos",
    )
    parser.add_argument("--dwsim-home", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.target.exists():
        print(f"[FAIL] objetivo inexistente: {args.target}")
        return 1
    case_dirs = list(iter_case_dirs(args.target))
    if not case_dirs:
        print(f"[FAIL] no se encontraron casos bajo: {args.target}")
        return 1
    results = [
        validate_case(
            case_dir,
            source=args.source,
            validator=args.validator,
            dwsim_home=args.dwsim_home,
        )
        for case_dir in case_dirs
    ]
    if args.write_artifacts:
        for case_dir, result in zip(case_dirs, results, strict=True):
            write_artifacts(case_dir, result)
    _print_results(results)
    return int(
        any(result_exit_code(result, strict=args.strict) for result in results)
    )


if __name__ == "__main__":
    sys.exit(main())
