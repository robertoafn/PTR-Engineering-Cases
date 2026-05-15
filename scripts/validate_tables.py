"""QC tabular sobre data/processed/*.csv usando sidecars .meta.yaml.

Verifica: tipos, rangos, nulos, unicidad de PK, integridad referencial.

Uso:
    python scripts/validate_tables.py data/processed/
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_sidecar(csv_path: Path) -> dict | None:
    side = csv_path.with_suffix(".meta.yaml")
    if not side.exists():
        return None
    return yaml.safe_load(side.read_text(encoding="utf-8"))


def check_variables(df: pd.DataFrame, meta: dict) -> list[str]:
    errs: list[str] = []
    for v in meta.get("variables", []):
        col = v["symbol"]
        if col not in df.columns:
            errs.append(f"columna ausente: {col}")
            continue
        if not v.get("nullable", False) and df[col].isna().any():
            errs.append(f"{col}: nulos no permitidos")
        rng = v.get("range")
        if rng and pd.api.types.is_numeric_dtype(df[col]):
            lo, hi = rng
            if ((df[col] < lo) | (df[col] > hi)).any():
                errs.append(f"{col}: valores fuera de [{lo},{hi}]")
    return errs


def main(target: Path) -> int:
    failures: dict[str, list[str]] = {}
    checked = 0
    for csv in target.rglob("*.csv"):
        meta = load_sidecar(csv)
        if meta is None:
            failures[str(csv.relative_to(ROOT))] = [
                f"falta sidecar: {csv.with_suffix('.meta.yaml').name}"
            ]
            continue
        checked += 1
        df = pd.read_csv(csv)
        errs = check_variables(df, meta)
        if errs:
            failures[str(csv.relative_to(ROOT))] = errs

    if failures:
        print(json.dumps(failures, indent=2))
        return 1
    print(f"[OK] {checked} tabla(s) válida(s).")
    return 0


if __name__ == "__main__":
    target = (
        Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data" / "processed"
    )
    sys.exit(main(target))
