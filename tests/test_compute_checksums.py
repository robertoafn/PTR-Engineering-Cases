"""Tests para scripts/compute_checksums.py."""
from __future__ import annotations

import hashlib
from pathlib import Path

from scripts.compute_checksums import _resolve_entity_path, iter_case_dirs, sha256


def test_sha256_matches_hashlib(tmp_path: Path) -> None:
    p = tmp_path / "sample.bin"
    payload = b"PTR-Engineering-Cases v0.1.0"
    p.write_bytes(payload)
    expected = hashlib.sha256(payload).hexdigest()
    assert sha256(p) == expected


def test_sha256_handles_empty_file(tmp_path: Path) -> None:
    p = tmp_path / "empty.txt"
    p.write_bytes(b"")
    assert sha256(p) == hashlib.sha256(b"").hexdigest()


def test_iter_case_dirs_accepts_single_case_directory(tmp_path: Path) -> None:
    case_dir = tmp_path / "003_case"
    case_dir.mkdir()
    (case_dir / "provenance.json").write_text("{}", encoding="utf-8")
    assert list(iter_case_dirs(case_dir)) == [case_dir]


def test_iter_case_dirs_discovers_cases_below_parent(tmp_path: Path) -> None:
    case_1 = tmp_path / "cases" / "001_case"
    case_2 = tmp_path / "cases" / "002_case"
    case_1.mkdir(parents=True)
    case_2.mkdir(parents=True)
    (case_1 / "provenance.json").write_text("{}", encoding="utf-8")
    (case_2 / "provenance.json").write_text("{}", encoding="utf-8")
    assert list(iter_case_dirs(tmp_path / "cases")) == [case_1, case_2]


def test_resolve_entity_path_rejects_escape(tmp_path: Path) -> None:
    case_dir = tmp_path / "003_case"
    case_dir.mkdir()
    assert _resolve_entity_path(case_dir, "../outside.csv") is None
