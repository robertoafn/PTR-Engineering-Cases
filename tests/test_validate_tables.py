"""Tests para scripts/validate_tables.py."""
from __future__ import annotations

import pandas as pd

from scripts.validate_tables import check_variables


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
