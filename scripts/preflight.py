"""Ejecuta el mismo control previo local que exige la integración continua.

El objetivo puede ser ``cases/`` o un directorio de caso individual. El comando
está diseñado para usarse desde ChatGPT Desktop, terminales Windows y CI.

Uso:
    python scripts/preflight.py cases/
    python scripts/preflight.py cases/001_slug/
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str]) -> int:
    print("\n$", " ".join(command))
    completed = subprocess.run(command, cwd=ROOT, check=False)
    return completed.returncode


def main(argv: list[str]) -> int:
    target = argv[1] if len(argv) > 1 else "cases/"
    python = sys.executable

    commands = [
        [python, "scripts/enforce_naming.py"],
        [python, "scripts/validate_metadata.py", target],
        [python, "scripts/validate_tables.py", target],
        [python, "scripts/unit_consistency_check.py", target],
        [python, "scripts/compute_checksums.py", "--verify", target],
        [python, "-m", "pytest", "tests/", "-q"],
        [python, "-m", "ruff", "check", "."],
    ]

    failures: list[list[str]] = []
    for command in commands:
        if run(command) != 0:
            failures.append(command)

    if failures:
        print("\n[FAIL] preflight incompleto. Comandos fallidos:")
        for command in failures:
            print(" -", " ".join(command))
        return 1

    print("\n[OK] preflight completo: el caso está listo para Pull Request.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
