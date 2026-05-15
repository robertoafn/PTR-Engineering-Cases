"""Tests para scripts/compute_checksums.py."""
from __future__ import annotations

import hashlib
from pathlib import Path

from scripts.compute_checksums import sha256


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
