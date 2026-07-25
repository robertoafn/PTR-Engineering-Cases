"""Tests para scripts/validate_tables.py."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from scripts.validate_tables import check_primary_key, check_variables, main


def test_check_variables_detects_null_in_non_nullable_column() -> None:
    df = pd.DataFrame({"T": [300.0, None, 320.0]})
    meta = {"variables": [{"symbol": "T", "name": "temperature",
                           "unit": "K", "type": "float", "nullable": False}]}
    errs = check_variables(df, meta)
    assert any("nulos no permitidos" in e for e in errs)


def test_check_variables_detects_out_of_range() -> None:
    df = pd.DataFrame({"x": [0.1, 0.5, 1.5]})
    meta = {"variables": [{"symbol": "x", "name": "fraction",
                           "unit": "dimensionless", "type": "float",
                           "range": [0, 1]}]}
    errs = check_variables(df, meta)
    assert any("fuera de" in e for e in errs)


def test_check_variables_passes_when_clean() -> None:
    df = pd.DataFrame({"T": [300.0, 310.0]})
    meta = {"variables": [{"symbol": "T", "name": "temperature",
                           "unit": "K", "type": "float"}]}
    assert check_variables(df, meta) == []


def test_check_variables_uses_explicit_csv_column() -> None:
    df = pd.DataFrame({"temperature_K": [300.0, 310.0]})
    meta = {
        "variables": [{
            "symbol": "T",
            "column": "temperature_K",
            "name": "temperature",
            "unit": "K",
            "type": "float",
        }]
    }
    assert check_variables(df, meta) == []


def test_check_variables_detects_declared_type_mismatch() -> None:
    df = pd.DataFrame({"temperature_K": ["cold", "hot"]})
    meta = {
        "variables": [{
            "symbol": "T",
            "column": "temperature_K",
            "name": "temperature",
            "unit": "K",
            "type": "float",
        }]
    }
    errs = check_variables(df, meta)
    assert any("tipo incompatible" in error for error in errs)


def test_main_fails_when_no_managed_datasets(tmp_path: Path) -> None:
    assert main(tmp_path) == 1


def test_check_variables_detects_undocumented_column() -> None:
    df = pd.DataFrame({"object_id": ["A"], "unexpected": [1]})
    meta = {
        "variables": [{
            "symbol": "object_id",
            "column": "object_id",
            "name": "identifier",
            "unit": "dimensionless",
            "type": "string",
        }]
    }
    errs = check_variables(df, meta)
    assert any("columna sin metadatos: unexpected" in error for error in errs)


def test_primary_key_detects_duplicates() -> None:
    df = pd.DataFrame({"object_id": ["A", "A"]})
    errs = check_primary_key(df, {"primary_key": ["object_id"]})
    assert any("duplicados" in error for error in errs)
