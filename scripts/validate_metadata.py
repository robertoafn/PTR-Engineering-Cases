"""Valida metadata.yaml de cada caso contra case_metadata.schema.json.

Uso:
    python scripts/validate_metadata.py cases/
    python scripts/validate_metadata.py cases/001_slug/

Salida:
    - Exit code 0 si todos válidos.
    - Exit code 1 + reporte JSON en tests/reports/metadata_<ts>.json si fallan.
"""
from __future__ import annotations

import datetime
import json
import sys
from collections.abc import Iterable
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "case_metadata.schema.json"
REPORTS = ROOT / "tests" / "reports"


def iter_metadata(target: Path) -> Iterable[Path]:
    if target.is_file():
        if target.name == "metadata.yaml":
            yield target
        return
    if target.exists() and target.is_dir():
        yield from sorted(target.rglob("metadata.yaml"))


def validate(target: Path) -> int:
    if not target.exists():
        print(f"[FAIL] objetivo inexistente: {target}")
        return 1
    try:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[FAIL] schema de casos no legible: {exc}")
        return 1
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    failures: list[dict] = []
    checked = 0
    for path in iter_metadata(target):
        checked += 1
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except (OSError, yaml.YAMLError) as exc:
            failures.append({
                "file": str(path),
                "errors": [{"path": [], "message": f"YAML no legible: {exc}"}],
            })
            continue
        errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
        if errors:
            failures.append({
                "file": str(path.relative_to(ROOT)),
                "errors": [
                    {"path": list(e.path), "message": e.message} for e in errors
                ],
            })

    if checked == 0:
        print(f"[FAIL] no se encontraron metadata.yaml en: {target}")
        return 1
    if failures:
        REPORTS.mkdir(parents=True, exist_ok=True)
        ts = datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%SZ")
        out = REPORTS / f"metadata_{ts}.json"
        out.write_text(json.dumps(failures, indent=2), encoding="utf-8")
        print(f"[FAIL] {len(failures)} archivo(s) con errores. Detalle: {out}")
        return 1
    print(f"[OK] {checked} metadata file(s) valid.")
    return 0


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "cases"
    sys.exit(validate(target))
