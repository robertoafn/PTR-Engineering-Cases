"""Calcula o verifica SHA-256 de artefactos declarados en provenance.json.

Acepta como objetivo:
- el directorio raíz ``cases/``;
- uno o más directorios de caso;
- un archivo ``provenance.json``.

Modos:
    Escritura (default): actualiza ``checksum_sha256`` en ``provenance.json``.
    Verificación (``--verify``): falla si el hash recalculado difiere del almacenado.

Uso:
    python scripts/compute_checksums.py cases/
    python scripts/compute_checksums.py cases/001_slug/
    python scripts/compute_checksums.py --verify cases/001_slug/
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
    """Calcula SHA-256 leyendo el archivo por bloques."""
    h = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(BUF), b""):
            h.update(chunk)
    return h.hexdigest()


def iter_case_dirs(target: Path) -> Iterable[Path]:
    """Descubre directorios de caso sin devolver éxitos vacíos.

    Un directorio se considera caso cuando contiene ``provenance.json``.
    """
    if target.is_file():
        if target.name == "provenance.json":
            yield target.parent
        return

    if not target.exists() or not target.is_dir():
        return

    if (target / "provenance.json").is_file():
        yield target
        return

    seen: set[Path] = set()
    for provenance in sorted(target.rglob("provenance.json")):
        case_dir = provenance.parent
        if case_dir not in seen:
            seen.add(case_dir)
            yield case_dir


def _resolve_entity_path(case_dir: Path, relative_path: str) -> Path | None:
    """Resuelve una entidad y bloquea rutas que escapen del directorio del caso."""
    case_root = case_dir.resolve()
    path = (case_root / relative_path).resolve()
    try:
        path.relative_to(case_root)
    except ValueError:
        return None
    return path


def process_case(case_dir: Path, verify: bool) -> int:
    """Actualiza o verifica los artefactos de un caso."""
    provenance_path = case_dir / "provenance.json"
    try:
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[FAIL] {case_dir.name}: provenance.json no legible: {exc}")
        return 1

    mismatches: list[str] = []
    entities = provenance.get("entities", [])
    if not isinstance(entities, list):
        print(f"[FAIL] {case_dir.name}: 'entities' debe ser una lista.")
        return 1

    for entity in entities:
        relative_path = entity.get("path")
        if not relative_path:
            continue

        path = _resolve_entity_path(case_dir, relative_path)
        if path is None:
            mismatches.append(f"ruta fuera del caso: {relative_path}")
            continue
        if not path.is_file():
            mismatches.append(f"ausente: {relative_path}")
            continue

        actual = sha256(path)
        if verify:
            expected = entity.get("checksum_sha256")
            if actual != expected:
                mismatches.append(
                    f"{relative_path}: esperado {expected}, actual {actual}"
                )
        else:
            entity["checksum_sha256"] = actual

    if not verify:
        provenance_path.write_text(
            json.dumps(provenance, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    if mismatches:
        print(f"[FAIL] {case_dir.name}:")
        for mismatch in mismatches:
            print(" -", mismatch)
        return 1

    print(
        f"[OK] {case_dir.name}: checksums "
        + ("verificados" if verify else "actualizados")
    )
    return 0


def main(argv: list[str]) -> int:
    verify = "--verify" in argv
    raw_targets = [arg for arg in argv[1:] if not arg.startswith("--")]
    targets = [Path(arg) for arg in raw_targets] or [ROOT / "cases"]

    return_code = 0
    checked = 0
    for target in targets:
        case_dirs = list(iter_case_dirs(target))
        if not case_dirs:
            print(f"[FAIL] sin casos con provenance.json: {target}")
            return_code = 1
            continue

        for case_dir in case_dirs:
            checked += 1
            return_code |= process_case(case_dir, verify)

    if return_code == 0:
        mode = "verificados" if verify else "actualizados"
        print(f"[OK] checksums {mode} en {checked} caso(s).")
    return return_code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
