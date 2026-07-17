"""Valida datasets CSV y sidecars ``.meta.yaml`` de forma recursiva.

Verifica:
- existencia del sidecar;
- conformidad del sidecar con ``schemas/dataset.schema.json``;
- correspondencia columna ↔ variable;
- tipos, nulos y rangos declarados;
- unicidad y completitud de la clave primaria, cuando se declara;
- checksum SHA-256 del CSV.

Uso:
    python scripts/validate_tables.py cases/
    python scripts/validate_tables.py cases/001_slug/
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "dataset.schema.json"


def load_sidecar(csv_path: Path) -> dict[str, Any] | None:
    sidecar = csv_path.with_suffix(".meta.yaml")
    if not sidecar.exists():
        return None
    return yaml.safe_load(sidecar.read_text(encoding="utf-8")) or {}


def _column_name(variable: dict[str, Any]) -> str:
    return str(variable.get("column") or variable["symbol"])


def _is_valid_type(series: pd.Series, declared_type: str) -> bool:
    values = series.dropna()
    if values.empty:
        return True

    if declared_type == "float":
        return pd.to_numeric(values, errors="coerce").notna().all()
    if declared_type == "int":
        numeric = pd.to_numeric(values, errors="coerce")
        return numeric.notna().all() and ((numeric % 1) == 0).all()
    if declared_type == "string":
        return values.map(lambda value: isinstance(value, str)).all()
    if declared_type == "bool":
        return values.map(lambda value: isinstance(value, bool)).all()
    if declared_type == "datetime":
        parsed = pd.to_datetime(values, errors="coerce", utc=True)
        return parsed.notna().all()
    return False


def check_variables(df: pd.DataFrame, meta: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    variables = meta.get("variables", []) or []
    declared_columns: list[str] = []

    for variable in variables:
        column = _column_name(variable)
        declared_columns.append(column)

        if column not in df.columns:
            errors.append(
                f"columna ausente: {column} (símbolo {variable.get('symbol')})"
            )
            continue

        series = df[column]
        if not variable.get("nullable", False) and series.isna().any():
            errors.append(f"{column}: nulos no permitidos")

        declared_type = variable.get("type")
        if declared_type and not _is_valid_type(series, declared_type):
            errors.append(f"{column}: no cumple tipo declarado '{declared_type}'")

        value_range = variable.get("range")
        if value_range:
            numeric = pd.to_numeric(series, errors="coerce")
            non_null = numeric.dropna()
            lower, upper = value_range
            if ((non_null < lower) | (non_null > upper)).any():
                errors.append(f"{column}: valores fuera de [{lower},{upper}]")

    undocumented = sorted(set(df.columns) - set(declared_columns))
    for column in undocumented:
        errors.append(f"columna sin metadatos: {column}")

    return errors


def check_primary_key(df: pd.DataFrame, meta: dict[str, Any]) -> list[str]:
    primary_key = meta.get("primary_key")
    if not primary_key:
        return []

    columns = [primary_key] if isinstance(primary_key, str) else list(primary_key)
    missing = [column for column in columns if column not in df.columns]
    if missing:
        return [f"primary_key: columnas ausentes: {', '.join(missing)}"]

    errors: list[str] = []
    if df[columns].isna().any(axis=None):
        errors.append("primary_key: contiene nulos")
    if df.duplicated(subset=columns).any():
        errors.append(f"primary_key: valores duplicados en {columns}")
    return errors


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_sidecar(meta: dict[str, Any]) -> list[str]:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [
        f"sidecar schema {list(error.path)}: {error.message}"
        for error in sorted(
            validator.iter_errors(meta), key=lambda item: list(item.path)
        )
    ]


def validate_dataset(csv_path: Path) -> list[str]:
    meta = load_sidecar(csv_path)
    if meta is None:
        return [f"falta sidecar: {csv_path.with_suffix('.meta.yaml').name}"]

    errors = validate_sidecar(meta)
    if errors:
        return errors

    try:
        dataframe = pd.read_csv(csv_path)
    except Exception as exc:
        return [f"CSV no legible: {exc}"]

    errors.extend(check_variables(dataframe, meta))
    errors.extend(check_primary_key(dataframe, meta))

    expected = meta.get("checksum_sha256")
    actual = sha256(csv_path)
    if expected != actual:
        errors.append(f"checksum_sha256: esperado {expected}, actual {actual}")

    return errors


def main(target: Path) -> int:
    if not target.exists():
        print(f"[FAIL] objetivo inexistente: {target}")
        return 1

    csv_files = sorted(target.rglob("*.csv")) if target.is_dir() else []
    if target.is_file() and target.suffix.lower() == ".csv":
        csv_files = [target]

    if not csv_files:
        print(f"[FAIL] no se encontraron datasets CSV en: {target}")
        return 1

    failures: dict[str, list[str]] = {}
    for csv_path in csv_files:
        errors = validate_dataset(csv_path)
        if errors:
            try:
                key = str(csv_path.relative_to(ROOT))
            except ValueError:
                key = str(csv_path)
            failures[key] = errors

    if failures:
        print(json.dumps(failures, indent=2, ensure_ascii=False))
        return 1

    print(f"[OK] {len(csv_files)} dataset(s) válido(s).")
    return 0


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "cases"
    sys.exit(main(target))
