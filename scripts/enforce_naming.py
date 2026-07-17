"""Aplica las convenciones definidas en ``docs/03_naming_conventions.md``.

Verifica carpetas de caso y artefactos tanto globales como contenidos dentro de
cada caso. Las plantillas y placeholders se excluyen explícitamente.

Uso:
    python scripts/enforce_naming.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PATTERNS = {
    "cases": re.compile(r"^\d{3}_[a-z0-9_]+$"),
    "datasets": re.compile(r"^[a-z0-9_]+_v\d{2}\.csv$"),
    "notebooks": re.compile(r"^\d{2}_[a-z0-9_]+\.ipynb$"),
    "scripts": re.compile(r"^[a-z][a-z0-9_]*\.py$"),
    "figures": re.compile(r"^fig_\d{3}_\d{2}_[a-z0-9_]+\.(png|svg|pdf)$"),
}

EXEMPT_NAMES = {"000_template", ".gitkeep", "__init__.py"}


def _is_exempt(path: Path) -> bool:
    return any(part in EXEMPT_NAMES for part in path.parts) or "templates" in path.parts


def _check_files(
    files: list[Path],
    pattern_name: str,
    label: str,
    bad: list[str],
) -> None:
    pattern = PATTERNS[pattern_name]
    for path in files:
        if _is_exempt(path):
            continue
        if not pattern.match(path.name):
            bad.append(f"{label}: {path.relative_to(ROOT)}")


def main() -> int:
    bad: list[str] = []
    cases_dir = ROOT / "cases"

    if cases_dir.exists():
        for path in cases_dir.iterdir():
            if not path.is_dir() or path.name in EXEMPT_NAMES:
                continue
            if not PATTERNS["cases"].match(path.name):
                bad.append(f"cases: {path.relative_to(ROOT)}")

    dataset_files: list[Path] = []
    processed = ROOT / "data" / "processed"
    if processed.exists():
        dataset_files.extend(processed.rglob("*.csv"))
    if cases_dir.exists():
        dataset_files.extend(cases_dir.rglob("*.csv"))
    _check_files(dataset_files, "datasets", "datasets", bad)

    notebook_files: list[Path] = []
    notebooks = ROOT / "notebooks"
    if notebooks.exists():
        notebook_files.extend(notebooks.rglob("*.ipynb"))
    if cases_dir.exists():
        notebook_files.extend(cases_dir.rglob("*.ipynb"))
    _check_files(notebook_files, "notebooks", "notebooks", bad)

    scripts = ROOT / "scripts"
    if scripts.exists():
        script_files = [path for path in scripts.glob("*.py") if path.is_file()]
        _check_files(script_files, "scripts", "scripts", bad)

    figure_files: list[Path] = []
    global_figures = ROOT / "assets" / "figures"
    if global_figures.exists():
        figure_files.extend(
            path
            for path in global_figures.rglob("*")
            if path.is_file() and path.suffix.lower() in {".png", ".svg", ".pdf"}
        )
    if cases_dir.exists():
        figure_files.extend(
            path
            for path in cases_dir.rglob("*")
            if path.is_file()
            and "assets" in path.parts
            and "figures" in path.parts
            and path.suffix.lower() in {".png", ".svg", ".pdf"}
        )
    _check_files(figure_files, "figures", "figures", bad)

    if bad:
        print("[FAIL] Naming violations:")
        for violation in bad:
            print(" -", violation)
        return 1

    print("[OK] naming conforme.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
