"""Tests para scripts/unit_consistency_check.py."""
from __future__ import annotations

from pathlib import Path

import yaml

from scripts.unit_consistency_check import _load_vocab, scan_metadata, scan_sidecar  # type: ignore

ROOT = Path(__file__).resolve().parents[1]


def test_vocab_loads_allowed_and_forbidden() -> None:
    allowed, forbidden = _load_vocab()
    assert "K" in allowed
    assert "Pa" in allowed
    assert "psi" in forbidden
    assert "atm" in forbidden


def test_scan_metadata_flags_forbidden_unit(tmp_path: Path) -> None:
    p = tmp_path / "metadata.yaml"
    yaml.safe_dump(
        {"inputs": [{"units": {"P": "psi"}}]},
        p.open("w", encoding="utf-8"),
    )
    allowed, forbidden = _load_vocab()
    bad = scan_metadata(p, allowed, forbidden)
    assert any("prohibida" in b for b in bad)


def test_scan_sidecar_passes_si(tmp_path: Path) -> None:
    p = tmp_path / "dataset_v01.meta.yaml"
    yaml.safe_dump(
        {"variables": [{"symbol": "T", "unit": "K"}]},
        p.open("w", encoding="utf-8"),
    )
    allowed, forbidden = _load_vocab()
    assert scan_sidecar(p, allowed, forbidden) == []
