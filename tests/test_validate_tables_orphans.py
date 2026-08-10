from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load_module():
    path = ROOT / "scripts" / "validate_tables.py"
    spec = importlib.util.spec_from_file_location("validate_tables_orphan_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_orphan_csv_is_a_validation_failure(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    validator = _load_module()
    orphan = tmp_path / "orphan_v01.csv"
    orphan.write_text("value\n1\n", encoding="utf-8")

    code = validator.main(tmp_path)

    assert code == 1
    payload = json.loads(capsys.readouterr().out)
    assert str(orphan) in payload
    assert payload[str(orphan)] == [
        "falta sidecar para CSV: orphan_v01.meta.yaml"
    ]


def test_single_orphan_csv_is_not_silently_ignored(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    validator = _load_module()
    orphan = tmp_path / "single_v01.csv"
    orphan.write_text("value\n1\n", encoding="utf-8")

    code = validator.main(orphan)

    assert code == 1
    assert "single_v01.meta.yaml" in capsys.readouterr().out
