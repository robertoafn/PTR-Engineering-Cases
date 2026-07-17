"""Verifica unidades declaradas contra el vocabulario controlado del repositorio.

Revisa ``metadata.yaml`` y sidecars ``*.meta.yaml`` de forma recursiva. Falla si
el objetivo no existe o no contiene archivos declarativos.

Uso:
    python scripts/unit_consistency_check.py cases/
    python scripts/unit_consistency_check.py cases/001_slug/
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
    for group in ("base_si", "derived_si", "allowed_non_si"):
        for unit in vocab.get(group, []) or []:
            allowed.add(unit["symbol"])
    forbidden = set(vocab.get("forbidden", []) or [])
    return allowed, forbidden


def _check_units_dict(
    units: dict,
    source: str,
    allowed: set[str],
    forbidden: set[str],
) -> list[str]:
    bad: list[str] = []
    for symbol, unit in (units or {}).items():
        if unit in forbidden:
            bad.append(f"{source}: unidad prohibida '{unit}' en {symbol}")
        elif unit not in allowed:
            bad.append(f"{source}: unidad fuera de vocabulario '{unit}' en {symbol}")
    return bad


def scan_metadata(path: Path, allowed: set[str], forbidden: set[str]) -> list[str]:
    meta = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    bad: list[str] = []
    for item in meta.get("inputs", []) or []:
        bad.extend(
            _check_units_dict(
                item.get("units") or {},
                str(path),
                allowed,
                forbidden,
            )
        )
    return bad


def scan_sidecar(path: Path, allowed: set[str], forbidden: set[str]) -> list[str]:
    meta = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    bad: list[str] = []
    for variable in meta.get("variables", []) or []:
        unit = variable.get("unit")
        symbol = variable.get("symbol")
        if unit in forbidden:
            bad.append(f"{path}: unidad prohibida '{unit}' en variable {symbol}")
        elif unit and unit not in allowed:
            bad.append(
                f"{path}: unidad fuera de vocabulario '{unit}' en variable {symbol}"
            )
    return bad


def main(target: Path) -> int:
    if not target.exists():
        print(f"[FAIL] objetivo inexistente: {target}")
        return 1

    allowed, forbidden = _load_vocab()
    metadata_files = sorted(target.rglob("metadata.yaml")) if target.is_dir() else []
    sidecar_files = sorted(target.rglob("*.meta.yaml")) if target.is_dir() else []

    if target.is_file() and target.name == "metadata.yaml":
        metadata_files = [target]
    elif target.is_file() and target.name.endswith(".meta.yaml"):
        sidecar_files = [target]

    checked = len(metadata_files) + len(sidecar_files)
    if checked == 0:
        print(f"[FAIL] no se encontraron archivos de unidades en: {target}")
        return 1

    bad: list[str] = []
    for path in metadata_files:
        bad.extend(scan_metadata(path, allowed, forbidden))
    for path in sidecar_files:
        bad.extend(scan_sidecar(path, allowed, forbidden))

    if bad:
        for error in bad:
            print(error)
        return 1

    print(f"[OK] unidades consistentes en {checked} archivo(s).")
    return 0


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "cases"
    sys.exit(main(target))
