"""Pruebas de integración para el preflight del repositorio."""

from __future__ import annotations

import sys

from scripts import preflight


def test_preflight_validates_published_literature_without_local_corpus(
    monkeypatch,
) -> None:
    executed: list[list[str]] = []

    def record_success(command: list[str]) -> int:
        executed.append(command)
        return 0

    monkeypatch.setattr(preflight, "run", record_success)

    assert preflight.main(["preflight.py", "cases/"]) == 0
    assert [
        sys.executable,
        "scripts/validate_literature_case.py",
        "Literature_cases/",
    ] in executed
    assert all("--corpus-case" not in command for command in executed)
