"""Tests para scripts/compute_checksums.py."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.compute_checksums import iter_case_dirs, main, sha256


def _make_case(root: Path, name: str = "001_test") -> Path:
    case_dir = root / name
    case_dir.mkdir(parents=True)
    artifact = case_dir / "artifact.txt"
    artifact.write_text("PTR\n", encoding="utf-8")
    provenance = {
        "entities": [
            {
                "path": "artifact.txt",
                "checksum_sha256": sha256(artifact),
            }
        ]
    }
    (case_dir / "provenance.json").write_text(
        json.dumps(provenance),
        encoding="utf-8",
    )
    return case_dir


def test_sha256_matches_hashlib(tmp_path: Path) -> None:
    path = tmp_path / "sample.bin"
    payload = b"PTR-Engineering-Cases v0.1.0"
    path.write_bytes(payload)
    expected = hashlib.sha256(payload).hexdigest()
    assert sha256(path) == expected


def test_sha256_handles_empty_file(tmp_path: Path) -> None:
    path = tmp_path / "empty.txt"
    path.write_bytes(b"")
    assert sha256(path) == hashlib.sha256(b"").hexdigest()


def test_iter_case_dirs_accepts_case_root(tmp_path: Path) -> None:
    case_dir = _make_case(tmp_path)
    assert list(iter_case_dirs(case_dir)) == [case_dir]


def test_iter_case_dirs_accepts_cases_parent(tmp_path: Path) -> None:
    cases_dir = tmp_path / "cases"
    case_dir = _make_case(cases_dir)
    assert list(iter_case_dirs(cases_dir)) == [case_dir]


def test_main_verifies_individual_case(tmp_path: Path) -> None:
    case_dir = _make_case(tmp_path)
    assert main(["compute_checksums.py", "--verify", str(case_dir)]) == 0


def test_main_fails_for_empty_or_invalid_target(tmp_path: Path) -> None:
    assert main(["compute_checksums.py", "--verify", str(tmp_path)]) == 1
