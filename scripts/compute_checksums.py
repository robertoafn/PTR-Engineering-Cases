"""Calcula/verifica SHA-256 de artefactos declarados en provenance.json.

Modos:
    Escritura (default): actualiza checksum_sha256 en provenance.json.
    Verificación (--verify): falla si el hash recalculado != almacenado.

Uso:
    python scripts/compute_checksums.py cases/
    python scripts/compute_checksums.py --verify cases/
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUF = 1 << 20  # 1 MiB


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(BUF), b""):
            h.update(chunk)
    return h.hexdigest()


def process_case(case_dir: Path, verify: bool) -> int:
    prov_path = case_dir / "provenance.json"
    if not prov_path.exists():
        return 0
    prov = json.loads(prov_path.read_text(encoding="utf-8"))
    mismatches: list[str] = []
    for ent in prov.get("entities", []):
        rel = ent.get("path")
        if not rel:
            continue
        p = (case_dir / rel).resolve()
        if not p.exists():
            mismatches.append(f"ausente: {rel}")
            continue
        actual = sha256(p)
        if verify:
            expected = ent.get("checksum_sha256")
            if actual != expected:
                mismatches.append(
                    f"{rel}: esperado {expected}, actual {actual}"
                )
        else:
            ent["checksum_sha256"] = actual

    if not verify:
        prov_path.write_text(
            json.dumps(prov, indent=2) + "\n", encoding="utf-8"
        )

    if mismatches:
        print(f"[FAIL] {case_dir.name}:")
        for m in mismatches:
            print(" -", m)
        return 1
    return 0


def main(argv: list[str]) -> int:
    verify = "--verify" in argv
    targets = [a for a in argv[1:] if not a.startswith("--")] or [
        str(ROOT / "cases")
    ]
    rc = 0
    for t in targets:
        base = Path(t)
        if not base.exists():
            continue
        for case in base.iterdir():
            if case.is_dir():
                rc |= process_case(case, verify)
    if rc == 0:
        print("[OK] checksums " + ("verificados" if verify else "actualizados"))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
