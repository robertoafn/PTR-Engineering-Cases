"""Tests para scripts/validate_tables.py."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from scripts.validate_tables import (
    check_primary_key,
    check_variables,
    sha256,
    validate_dataset,
)


def test_check_variables_maps_column_to_symbol() -> None:
    dataframe = pd.DataFrame({"temperature_K": [300.0, 310.0]})
    meta = {
        "variables": [
            {
                "symbol": "T",
                "column": "temperature_K",
                "name": "temperature",
                "unit": "K",
                "type": "float",
                "nullable": False,
            }
        ]
    }
    assert check_variables(dataframe, meta) == []


def test_check_variables_detects_null_and_range() -> None:
    dataframe = pd.DataFrame({"temperature_K": [300.0, None, 500.0]})
    meta = {
        "variables": [
            {
                "symbol": "T",
                "column": "temperature_K",
                "name": "temperature",
                "unit": "K",
                "type": "float",
                "nullable": False,
                "range": [250.0, 400.0],
            }
        ]
    }
    errors = check_variables(dataframe, meta)
    assert any("nulos no permitidos" in error for error in errors)
    assert any("fuera de" in error for error in errors)


def test_check_variables_detects_undocumented_column() -> None:
    dataframe = pd.DataFrame({"T": [300.0], "unexpected": [1]})
    meta = {
        "variables": [
            {
                "symbol": "T",
                "name": "temperature",
                "unit": "K",
                "type": "float",
            }
        ]
    }
    errors = check_variables(dataframe, meta)
    assert any("columna sin metadatos: unexpected" in error for error in errors)


def test_primary_key_detects_duplicates() -> None:
    dataframe = pd.DataFrame({"object_id": ["A", "A"]})
    errors = check_primary_key(dataframe, {"primary_key": ["object_id"]})
    assert any("duplicados" in error for error in errors)


def test_validate_dataset_checks_sidecar_and_checksum(tmp_path: Path) -> None:
    csv_path = tmp_path / "results_v01.csv"
    csv_path.write_text("object_id,temperature_K\nA,300.0\n", encoding="utf-8")
    sidecar = {
        "dataset_id": "results_v01",
        "case_id": "001_test",
        "source_type": "simulated",
        "variables": [
            {
                "symbol": "object_id",
                "column": "object_id",
                "name": "identifier",
                "unit": "dimensionless",
                "type": "string",
                "nullable": False,
            },
            {
                "symbol": "T",
                "column": "temperature_K",
                "name": "temperature",
                "unit": "K",
                "type": "float",
                "nullable": False,
                "range": [250.0, 400.0],
            },
        ],
        "primary_key": ["object_id"],
        "created_at": "2026-07-17T00:00:00Z",
        "version": "0.1.0",
        "checksum_sha256": sha256(csv_path),
    }
    csv_path.with_suffix(".meta.yaml").write_text(
        yaml.safe_dump(sidecar, sort_keys=False),
        encoding="utf-8",
    )
    assert validate_dataset(csv_path) == []
