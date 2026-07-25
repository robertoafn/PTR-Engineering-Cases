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
from collections.abc import Iterable
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUF = 1 << 20  # 1 MiB


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(BUF), b""):
            h.update(chunk)
    return h.hexdigest()


def iter_case_dirs(target: Path) -> Iterable[Path]:
    """Yield case directories for either one case or a parent directory."""
    if target.is_file():
        if target.name == "provenance.json":
            yield target.parent
        return
    if not target.is_dir():
        return
    if (target / "provenance.json").is_file():
        yield target
        return
    for prov_path in sorted(target.rglob("provenance.json")):
        yield prov_path.parent


def _resolve_entity_path(case_dir: Path, relative_path: str) -> Path | None:
    """Resolve an entity path while preventing escape from the case."""
    case_root = case_dir.resolve()
    path = (case_root / relative_path).resolve()
    try:
        path.relative_to(case_root)
    except ValueError:
        return None
    return path


def process_case(case_dir: Path, verify: bool) -> int:
    prov_path = case_dir / "provenance.json"
    try:
        prov = json.loads(prov_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[FAIL] {case_dir.name}: provenance.json no legible: {exc}")
        return 1
    mismatches: list[str] = []
    entities = prov.get("entities", [])
    if not isinstance(entities, list):
        print(f"[FAIL] {case_dir.name}: 'entities' debe ser una lista")
        return 1
    for ent in entities:
        rel = ent.get("path")
        if not rel:
            continue
        p = _resolve_entity_path(case_dir, rel)
        if p is None:
            mismatches.append(f"ruta fuera del caso: {rel}")
            continue
        if not p.is_file():
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
            json.dumps(prov, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
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
            print(f"[FAIL] ruta ausente: {base}")
            rc = 1
            continue
        cases = list(iter_case_dirs(base))
        if not cases:
            print(f"[FAIL] sin provenance.json bajo: {base}")
            rc = 1
            continue
        for case in cases:
            rc |= process_case(case, verify)
    if rc == 0:
        print("[OK] checksums " + ("verificados" if verify else "actualizados"))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
