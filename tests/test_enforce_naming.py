"""Tests para scripts/enforce_naming.py."""
from __future__ import annotations

from scripts.enforce_naming import PATTERNS


def test_case_folder_pattern_accepts_valid() -> None:
    assert PATTERNS["cases"].match("001_flash_binario_etanol_agua")


def test_case_folder_pattern_rejects_invalid() -> None:
    assert not PATTERNS["cases"].match("Flash Binario")
    assert not PATTERNS["cases"].match("1_slug")
    assert not PATTERNS["cases"].match("001-flash")


def test_dataset_pattern() -> None:
    assert PATTERNS["datasets"].match("vle_etoh_water_v01.csv")
    assert not PATTERNS["datasets"].match("VLE_etoh_v1.csv")
    assert not PATTERNS["datasets"].match("vle.csv")


def test_notebook_pattern() -> None:
    assert PATTERNS["notebooks"].match("02_calculo_k_values.ipynb")
    assert not PATTERNS["notebooks"].match("notebook.ipynb")


def test_script_pattern() -> None:
    assert PATTERNS["scripts"].match("validate_metadata.py")
    assert not PATTERNS["scripts"].match("Validate-Metadata.py")


def test_figure_pattern() -> None:
    assert PATTERNS["figures"].match("fig_001_03_parity_plot.png")
    assert not PATTERNS["figures"].match("plot.png")
