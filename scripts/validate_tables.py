"""QC tabular sobre datasets canónicos que tienen sidecar .meta.yaml.

Verifica: schema del sidecar, columnas, tipos, rangos, nulos, checksum,
unicidad de (case_id, dataset_id), integridad sidecar-caso y ausencia de CSV
canónicos versionados con patrón de nombre *_vNN.csv sin sidecar.

Uso:
    python scripts/validate_tables.py cases/
    python scripts/validate_tables.py cases/003_slug/
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import pandas as pd
import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "dataset.schema.json"
VERSIONED_CSV = re.compile(r"_v[0-9]+\.csv$", re.IGNORECASE)


def load_sidecar(csv_path: Path) -> dict | None:
    side = csv_path.with_suffix(".meta.yaml")
    if not side.exists():
        return None
    return yaml.safe_load(side.read_text(encoding="utf-8"))


def iter_sidecars(target: Path):
    if target.is_file():
        if target.name.endswith(".meta.yaml"):
            yield target
        elif target.suffix == ".csv":
            sidecar = target.with_suffix(".meta.yaml")
            if sidecar.is_file():
                yield sidecar
        return
    yield from sorted(target.rglob("*.meta.yaml"))


def iter_versioned_csvs(target: Path):
    if target.is_file():
        if target.suffix.lower() == ".csv" and VERSIONED_CSV.search(target.name):
            yield target
        elif target.name.endswith(".meta.yaml"):
            csv = csv_for_sidecar(target)
            if csv.is_file():
                yield csv
        return
    yield from sorted(
        csv for csv in target.rglob("*.csv") if VERSIONED_CSV.search(csv.name)
    )


def csv_for_sidecar(sidecar: Path) -> Path:
    stem = sidecar.name.removesuffix(".meta.yaml")
    return sidecar.with_name(f"{stem}.csv")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _column_has_type(series: pd.Series, expected: str) -> bool:
    non_null = series.dropna()
    if expected == "float":
        return pd.api.types.is_numeric_dtype(non_null)
    if expected == "int":
        if not pd.api.types.is_numeric_dtype(non_null):
            return False
        return bool((non_null % 1 == 0).all())
    if expected == "string":
        return pd.api.types.is_string_dtype(non_null)
    if expected == "bool":
        return pd.api.types.is_bool_dtype(non_null)
    if expected == "datetime":
        return bool(pd.to_datetime(non_null, errors="coerce").notna().all())
    return False


def check_variables(df: pd.DataFrame, meta: dict) -> list[str]:
    errs: list[str] = []
    declared_columns: list[str] = []
    for v in meta.get("variables", []):
        col = v.get("column", v["symbol"])
        declared_columns.append(col)
        if col not in df.columns:
            errs.append(f"columna ausente: {col}")
            continue
        if not v.get("nullable", False) and df[col].isna().any():
            errs.append(f"{col}: nulos no permitidos")
        expected_type = v.get("type")
        if expected_type and not _column_has_type(df[col], expected_type):
            errs.append(f"{col}: tipo incompatible con {expected_type}")
        rng = v.get("range")
        if rng and pd.api.types.is_numeric_dtype(df[col]):
            lo, hi = rng
            if ((df[col] < lo) | (df[col] > hi)).any():
                errs.append(f"{col}: valores fuera de [{lo},{hi}]")
    for col in sorted(set(df.columns) - set(declared_columns)):
        errs.append(f"columna sin metadatos: {col}")
    return errs


def check_primary_key(df: pd.DataFrame, meta: dict) -> list[str]:
    primary_key = meta.get("primary_key")
    if not primary_key:
        return []
    columns = [primary_key] if isinstance(primary_key, str) else list(primary_key)
    missing = [column for column in columns if column not in df.columns]
    if missing:
        return [f"primary_key: columnas ausentes: {', '.join(missing)}"]
    errs: list[str] = []
    if df[columns].isna().any(axis=None):
        errs.append("primary_key: contiene nulos")
    if df.duplicated(subset=columns).any():
        errs.append(f"primary_key: valores duplicados en {columns}")
    return errs


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _case_id_from_ancestor(path: Path) -> str | None:
    for parent in path.parents:
        metadata_path = parent / "metadata.yaml"
        if metadata_path.is_file():
            metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
            return metadata.get("case_id")
        if parent == ROOT:
            break
    return None


def main(target: Path) -> int:
    failures: dict[str, list[str]] = {}
    checked = 0
    seen_dataset_keys: set[tuple[str, str]] = set()
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    resolved_target = target.resolve()
    sidecars = list(iter_sidecars(resolved_target))
    orphan_csvs = [
        csv
        for csv in iter_versioned_csvs(resolved_target)
        if not csv.with_suffix(".meta.yaml").is_file()
    ]
    for csv in orphan_csvs:
        failures[_display_path(csv)] = [
            f"falta sidecar para CSV: {csv.with_suffix('.meta.yaml').name}"
        ]
    if not sidecars and not orphan_csvs:
        print(f"[FAIL] 0 datasets con sidecar bajo {_display_path(target)}.")
        return 1

    for sidecar in sidecars:
        csv = csv_for_sidecar(sidecar)
        rel_path = _display_path(csv)
        if not csv.is_file():
            failures[rel_path] = [f"falta CSV para sidecar: {sidecar.name}"]
            continue
        checked += 1
        meta = yaml.safe_load(sidecar.read_text(encoding="utf-8")) or {}
        errs = [
            f"sidecar schema {list(error.path)}: {error.message}"
            for error in sorted(
                validator.iter_errors(meta), key=lambda error: list(error.path)
            )
        ]
        df = pd.read_csv(csv)
        errs.extend(check_variables(df, meta))
        errs.extend(check_primary_key(df, meta))

        expected_checksum = meta.get("checksum_sha256")
        if expected_checksum and sha256(csv) != expected_checksum:
            errs.append("checksum_sha256 no coincide con el CSV")

        dataset_key = (meta.get("case_id", ""), meta.get("dataset_id", ""))
        if dataset_key in seen_dataset_keys:
            errs.append(f"dataset duplicado: {dataset_key}")
        seen_dataset_keys.add(dataset_key)

        ancestor_case_id = _case_id_from_ancestor(csv)
        if ancestor_case_id and meta.get("case_id") != ancestor_case_id:
            errs.append(
                f"case_id {meta.get('case_id')} no coincide con {ancestor_case_id}"
            )
        if errs:
            failures[rel_path] = errs

    if failures:
        print(json.dumps(failures, indent=2))
        return 1
    print(f"[OK] {checked} tabla(s) válida(s).")
    return 0


if __name__ == "__main__":
    target = (
        Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "cases"
    )
    sys.exit(main(target))
