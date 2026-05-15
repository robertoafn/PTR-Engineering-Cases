"""Verifica que toda unidad declarada exista en el vocabulario controlado SI
y que ninguna unidad prohibida aparezca en metadata o sidecars de datasets.

Uso:
    python scripts/unit_consistency_check.py cases/
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
VOCAB_PATH = ROOT / "schemas" / "units.controlled_vocabulary.yaml"


def _load_vocab() -> tuple[set[str], set[str]]:
    vocab = yaml.safe_load(VOCAB_PATH.read_text(encoding="utf-8"))
    allowed: set[str] = set()
    for grp in ("base_si", "derived_si", "allowed_non_si"):
        for u in vocab.get(grp, []) or []:
            allowed.add(u["symbol"])
    forbidden = set(vocab.get("forbidden", []) or [])
    return allowed, forbidden


def _check_units_dict(units: dict, source: str, allowed, forbidden) -> list[str]:
    bad: list[str] = []
    for sym, unit in (units or {}).items():
        if unit in forbidden:
            bad.append(f"{source}: unidad prohibida '{unit}' en {sym}")
        elif unit not in allowed:
            bad.append(
                f"{source}: unidad fuera de vocabulario '{unit}' en {sym}"
            )
    return bad


def scan_metadata(path: Path, allowed, forbidden) -> list[str]:
    meta = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    bad: list[str] = []
    for inp in meta.get("inputs", []) or []:
        bad.extend(
            _check_units_dict(
                inp.get("units") or {}, str(path), allowed, forbidden
            )
        )
    return bad


def scan_sidecar(path: Path, allowed, forbidden) -> list[str]:
    meta = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    bad: list[str] = []
    for v in meta.get("variables", []) or []:
        unit = v.get("unit")
        if unit in forbidden:
            bad.append(
                f"{path}: unidad prohibida '{unit}' en variable {v.get('symbol')}"
            )
        elif unit and unit not in allowed:
            bad.append(
                f"{path}: unidad fuera de vocabulario '{unit}' en variable {v.get('symbol')}"
            )
    return bad


def main(target: Path) -> int:
    allowed, forbidden = _load_vocab()
    bad: list[str] = []
    for p in target.rglob("metadata.yaml"):
        bad.extend(scan_metadata(p, allowed, forbidden))
    for p in target.rglob("*.meta.yaml"):
        bad.extend(scan_sidecar(p, allowed, forbidden))
    if bad:
        for b in bad:
            print(b)
        return 1
    print("[OK] unidades consistentes con vocabulario SI.")
    return 0


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "cases"
    sys.exit(main(target))
