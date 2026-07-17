"""Tests para scripts/unit_consistency_check.py."""
from __future__ import annotations

from pathlib import Path

import yaml

from scripts.unit_consistency_check import (
    _load_vocab,
    main,
    scan_metadata,
    scan_sidecar,
)

ROOT = Path(__file__).resolve().parents[1]


def test_vocab_loads_allowed_and_forbidden() -> None:
    allowed, forbidden = _load_vocab()
    assert "K" in allowed
    assert "Pa" in allowed
    assert "psi" in forbidden
    assert "atm" in forbidden


def test_scan_metadata_flags_forbidden_unit(tmp_path: Path) -> None:
    path = tmp_path / "metadata.yaml"
    yaml.safe_dump(
        {"inputs": [{"units": {"P": "psi"}}]},
        path.open("w", encoding="utf-8"),
    )
    allowed, forbidden = _load_vocab()
    bad = scan_metadata(path, allowed, forbidden)
    assert any("prohibida" in error for error in bad)


def test_scan_sidecar_passes_si(tmp_path: Path) -> None:
    path = tmp_path / "dataset_v01.meta.yaml"
    yaml.safe_dump(
        {"variables": [{"symbol": "T", "unit": "K"}]},
        path.open("w", encoding="utf-8"),
    )
    allowed, forbidden = _load_vocab()
    assert scan_sidecar(path, allowed, forbidden) == []


def test_main_rejects_empty_target(tmp_path: Path) -> None:
    assert main(tmp_path) == 1
