"""Aplica convenciones de nombres (docs/03_naming_conventions.md).

Verifica patrones para:
- carpetas de caso
- datasets CSV
- notebooks
- scripts Python
- figuras

Uso:
    python scripts/enforce_naming.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PATTERNS = {
    "cases":     re.compile(r"^\d{3}_[a-z0-9_]+$"),
    "datasets":  re.compile(r"^[a-z0-9_]+_v\d{2}\.csv$"),
    "notebooks": re.compile(r"^\d{2}_[a-z0-9_]+\.ipynb$"),
    "scripts":   re.compile(r"^[a-z][a-z0-9_]*\.py$"),
    "figures":   re.compile(r"^fig_\d{3}_\d{2}_[a-z0-9_]+\.(png|svg|pdf)$"),
}

# Carpetas/archivos exentos (placeholders, plantillas)
EXEMPT_NAMES = {"000_template", ".gitkeep", "__init__.py"}


def main() -> int:
    bad: list[str] = []

    # Carpetas de caso
    cases_dir = ROOT / "cases"
    if cases_dir.exists():
        for p in cases_dir.iterdir():
            if not p.is_dir() or p.name in EXEMPT_NAMES:
                continue
            if not PATTERNS["cases"].match(p.name):
                bad.append(f"cases: {p.relative_to(ROOT)}")

    # Datasets CSV
    processed = ROOT / "data" / "processed"
    if processed.exists():
        for p in processed.rglob("*.csv"):
            if not PATTERNS["datasets"].match(p.name):
                bad.append(f"datasets: {p.relative_to(ROOT)}")

    # Notebooks
    notebooks = ROOT / "notebooks"
    if notebooks.exists():
        for p in notebooks.rglob("*.ipynb"):
            if not PATTERNS["notebooks"].match(p.name):
                bad.append(f"notebooks: {p.relative_to(ROOT)}")

    # Scripts
    scripts = ROOT / "scripts"
    if scripts.exists():
        for p in scripts.glob("*.py"):
            if p.name in EXEMPT_NAMES:
                continue
            if not PATTERNS["scripts"].match(p.name):
                bad.append(f"scripts: {p.relative_to(ROOT)}")

    # Figuras
    figures = ROOT / "assets" / "figures"
    if figures.exists():
        for p in figures.rglob("*"):
            if p.is_file() and p.suffix.lower() in {".png", ".svg", ".pdf"}:
                if not PATTERNS["figures"].match(p.name):
                    bad.append(f"figures: {p.relative_to(ROOT)}")

    if bad:
        print("[FAIL] Naming violations:")
        for b in bad:
            print(" -", b)
        return 1
    print("[OK] naming conforme.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
