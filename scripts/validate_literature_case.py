"""Valida la integridad de los artefactos fuente de ``Literature_cases``.

El contrato de cada caso se declara en ``source_manifest.json``. El script
comprueba que las rutas permanezcan dentro del caso, que no estén duplicadas y
que tamaño y SHA-256 coincidan con los archivos publicados. De forma opcional,
también compara cada fuente byte a byte con el corpus local (ignorado por Git).

Uso::

    python scripts/validate_literature_case.py Literature_cases/
    python scripts/validate_literature_case.py "Literature_cases/102 - ..."
    python scripts/validate_literature_case.py "Literature_cases/102 - ..." \
        --corpus-case "references/Literature_cases_references/.../102 - ..."

Códigos de salida:

* 0: todos los casos cumplen el manifiesto.
* 1: existe una diferencia respecto del estado esperado.
* 2: la entrada o el contrato del manifiesto no son válidos.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any

MANIFEST_NAME = "source_manifest.json"
BUFFER_SIZE = 1 << 20
SHA256_PATTERN = re.compile(r"^[0-9a-fA-F]{64}$")
WINDOWS_DRIVE_PATTERN = re.compile(r"^[A-Za-z]:")
VALID_EXPECTED_STATUSES = frozenset({"present", "absent"})


class ContractError(ValueError):
    """Indica que la entrada o el manifiesto no cumplen el contrato."""


class DuplicateJsonKeyError(ContractError):
    """Indica que un objeto JSON contiene claves repetidas."""


@dataclass(frozen=True)
class FileSpec:
    """Expectativa normalizada para un archivo fuente."""

    relative_path: PurePosixPath
    display_path: str
    expected_status: str
    size_bytes: int | None
    sha256: str | None


@dataclass
class CaseValidation:
    """Resultado reproducible de la validación de un caso."""

    case_dir: Path
    checked_files: int = 0
    mismatches: list[str] = field(default_factory=list)
    contract_errors: list[str] = field(default_factory=list)

    @property
    def exit_code(self) -> int:
        if self.contract_errors:
            return 2
        if self.mismatches:
            return 1
        return 0


def sha256_file(path: Path) -> str:
    """Calcula SHA-256 leyendo el archivo en bloques."""

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(BUFFER_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def files_equal_bytewise(left: Path, right: Path) -> bool:
    """Compara contenido binario sin depender de cachés de tamaño o mtime."""

    if left.stat().st_size != right.stat().st_size:
        return False
    with left.open("rb") as left_stream, right.open("rb") as right_stream:
        while True:
            left_chunk = left_stream.read(BUFFER_SIZE)
            right_chunk = right_stream.read(BUFFER_SIZE)
            if left_chunk != right_chunk:
                return False
            if not left_chunk:
                return True


def _reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJsonKeyError(f"clave JSON duplicada: {key!r}")
        result[key] = value
    return result


def _safe_relative_path(raw_path: Any, *, entry_number: int) -> tuple[PurePosixPath, str]:
    if not isinstance(raw_path, str) or not raw_path:
        raise ContractError(f"files[{entry_number}].path debe ser texto no vacío")
    if raw_path != raw_path.strip() or "\x00" in raw_path:
        raise ContractError(f"files[{entry_number}].path contiene caracteres ambiguos")

    portable = raw_path.replace("\\", "/")
    if portable.startswith("/") or WINDOWS_DRIVE_PATTERN.match(portable):
        raise ContractError(f"files[{entry_number}].path debe ser relativa: {raw_path!r}")

    segments = portable.split("/")
    if any(segment in {"", ".", ".."} for segment in segments):
        raise ContractError(
            f"files[{entry_number}].path contiene escape o segmentos no canónicos: "
            f"{raw_path!r}"
        )
    return PurePosixPath(*segments), portable


def _parse_file_specs(document: Any) -> list[FileSpec]:
    if not isinstance(document, dict):
        raise ContractError("la raíz de source_manifest.json debe ser un objeto")
    raw_files = document.get("files")
    if not isinstance(raw_files, list) or not raw_files:
        raise ContractError("'files' debe ser una lista no vacía")

    specs: list[FileSpec] = []
    seen_paths: dict[str, str] = {}
    for index, entry in enumerate(raw_files):
        if not isinstance(entry, dict):
            raise ContractError(f"files[{index}] debe ser un objeto")

        relative_path, display_path = _safe_relative_path(entry.get("path"), entry_number=index)
        duplicate_key = unicodedata.normalize("NFC", display_path).casefold()
        if duplicate_key in seen_paths:
            raise ContractError(
                "rutas duplicadas en 'files': "
                f"{seen_paths[duplicate_key]!r} y {display_path!r}"
            )
        seen_paths[duplicate_key] = display_path

        raw_status = entry.get("expected_status", "present")
        if not isinstance(raw_status, str):
            raise ContractError(f"files[{index}].expected_status debe ser texto")
        expected_status = raw_status.strip().casefold()
        if expected_status not in VALID_EXPECTED_STATUSES:
            valid = ", ".join(sorted(VALID_EXPECTED_STATUSES))
            raise ContractError(
                f"files[{index}].expected_status={raw_status!r}; valores válidos: {valid}"
            )

        if "immutable" in entry and not isinstance(entry["immutable"], bool):
            raise ContractError(f"files[{index}].immutable debe ser booleano")

        if expected_status == "absent":
            if "size_bytes" in entry or "sha256" in entry:
                raise ContractError(
                    f"files[{index}] con expected_status='absent' no debe declarar "
                    "size_bytes ni sha256"
                )
            size_bytes = None
            expected_sha256 = None
        else:
            size_bytes = entry.get("size_bytes")
            if isinstance(size_bytes, bool) or not isinstance(size_bytes, int) or size_bytes < 0:
                raise ContractError(
                    f"files[{index}].size_bytes debe ser un entero no negativo"
                )

            raw_sha256 = entry.get("sha256")
            if not isinstance(raw_sha256, str) or not SHA256_PATTERN.fullmatch(raw_sha256):
                raise ContractError(f"files[{index}].sha256 debe contener 64 dígitos hexadecimales")
            expected_sha256 = raw_sha256.casefold()

        specs.append(
            FileSpec(
                relative_path=relative_path,
                display_path=display_path,
                expected_status=expected_status,
                size_bytes=size_bytes,
                sha256=expected_sha256,
            )
        )
    return specs


def load_manifest(manifest_path: Path) -> list[FileSpec]:
    """Carga y valida el contrato de un ``source_manifest.json``."""

    try:
        document = json.loads(
            manifest_path.read_text(encoding="utf-8-sig"),
            object_pairs_hook=_reject_duplicate_json_keys,
        )
    except DuplicateJsonKeyError:
        raise
    except FileNotFoundError as exc:
        raise ContractError(f"manifiesto ausente: {manifest_path}") from exc
    except OSError as exc:
        raise ContractError(f"no se pudo leer {manifest_path}: {exc}") from exc
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"JSON inválido en {manifest_path}: {exc}") from exc
    return _parse_file_specs(document)


def discover_case_dirs(target: Path) -> list[Path]:
    """Resuelve un manifiesto, un caso o la raíz completa de Literature_cases."""

    if target.is_file():
        if target.name != MANIFEST_NAME:
            raise ContractError(f"el archivo de entrada debe llamarse {MANIFEST_NAME}")
        return [target.parent]
    if not target.exists():
        raise ContractError(f"ruta de entrada ausente: {target}")
    if not target.is_dir():
        raise ContractError(f"la entrada no es archivo ni directorio válido: {target}")
    if (target / MANIFEST_NAME).is_file():
        return [target]

    # En la raíz de Literature_cases sólo los directorios inmediatos son casos.
    # README.md y otros archivos de índice de la raíz no participan del contrato.
    child_dirs = sorted(path for path in target.iterdir() if path.is_dir())
    if not child_dirs:
        raise ContractError(f"no se encontraron casos bajo: {target}")
    missing = [path.name for path in child_dirs if not (path / MANIFEST_NAME).is_file()]
    if missing:
        names = ", ".join(repr(name) for name in missing)
        raise ContractError(f"casos sin {MANIFEST_NAME}: {names}")
    return child_dirs


def _resolve_inside(root: Path, relative_path: PurePosixPath) -> Path:
    root_resolved = root.resolve()
    candidate = root_resolved.joinpath(*relative_path.parts).resolve()
    try:
        candidate.relative_to(root_resolved)
    except ValueError as exc:
        message = f"la ruta resuelta escapa del caso: {relative_path.as_posix()}"
        raise ContractError(message) from exc
    return candidate


def validate_case(case_dir: Path, corpus_case: Path | None = None) -> CaseValidation:
    """Valida un caso y, opcionalmente, su copia contra el corpus local."""

    result = CaseValidation(case_dir=case_dir)
    try:
        specs = load_manifest(case_dir / MANIFEST_NAME)
        if corpus_case is not None and not corpus_case.is_dir():
            raise ContractError(f"--corpus-case no es un directorio: {corpus_case}")
    except ContractError as exc:
        result.contract_errors.append(str(exc))
        return result

    for spec in specs:
        try:
            candidate = _resolve_inside(case_dir, spec.relative_path)
            corpus_file = (
                _resolve_inside(corpus_case, spec.relative_path)
                if corpus_case is not None
                else None
            )
        except (ContractError, OSError) as exc:
            result.contract_errors.append(f"{spec.display_path}: {exc}")
            continue

        if spec.expected_status == "absent":
            if candidate.exists():
                result.mismatches.append(f"{spec.display_path}: debía estar ausente")
            if corpus_file is not None and corpus_file.exists():
                result.mismatches.append(
                    f"{spec.display_path}: debía estar ausente también en el corpus"
                )
            continue

        result.checked_files += 1
        if not candidate.is_file():
            result.mismatches.append(f"{spec.display_path}: archivo ausente o no regular")
            continue

        try:
            actual_size = candidate.stat().st_size
            actual_sha256 = sha256_file(candidate)
        except OSError as exc:
            result.contract_errors.append(f"{spec.display_path}: no se pudo leer: {exc}")
            continue

        if actual_size != spec.size_bytes:
            result.mismatches.append(
                f"{spec.display_path}: tamaño esperado {spec.size_bytes}, actual {actual_size}"
            )
        if actual_sha256 != spec.sha256:
            result.mismatches.append(
                f"{spec.display_path}: SHA-256 esperado {spec.sha256}, actual {actual_sha256}"
            )

        if corpus_file is not None:
            if not corpus_file.is_file():
                result.mismatches.append(
                    f"{spec.display_path}: archivo ausente o no regular en el corpus"
                )
                continue
            try:
                identical = files_equal_bytewise(candidate, corpus_file)
            except OSError as exc:
                result.contract_errors.append(
                    f"{spec.display_path}: no se pudo comparar con el corpus: {exc}"
                )
                continue
            if not identical:
                result.mismatches.append(
                    f"{spec.display_path}: contenido distinto del corpus (comparación byte a byte)"
                )
    return result


def _print_result(result: CaseValidation) -> None:
    if result.exit_code == 0:
        print(f"[PASS] {result.case_dir.name}: {result.checked_files} archivo(s) verificado(s)")
        return
    label = "ERROR" if result.contract_errors else "MISMATCH"
    print(f"[{label}] {result.case_dir.name}")
    for message in result.contract_errors:
        print(f"  - contrato: {message}")
    for message in result.mismatches:
        print(f"  - diferencia: {message}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Valida source_manifest.json de uno o todos los Literature_cases."
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=str(Path(__file__).resolve().parents[1] / "Literature_cases"),
        help="source_manifest.json, carpeta de caso o raíz Literature_cases/",
    )
    parser.add_argument(
        "--corpus-case",
        type=Path,
        help=(
            "carpeta exacta del corpus para un caso; al validar varios casos, "
            "carpeta padre con subdirectorios del mismo nombre"
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        case_dirs = discover_case_dirs(Path(args.target))
        if args.corpus_case is not None and not args.corpus_case.is_dir():
            raise ContractError(f"--corpus-case no es un directorio: {args.corpus_case}")
    except (ContractError, OSError) as exc:
        print(f"[ERROR] {exc}")
        return 2

    aggregate_code = 0
    multiple_cases = len(case_dirs) > 1
    for case_dir in case_dirs:
        corpus_case = args.corpus_case
        if corpus_case is not None and multiple_cases:
            corpus_case = corpus_case / case_dir.name
        result = validate_case(case_dir, corpus_case)
        _print_result(result)
        aggregate_code = max(aggregate_code, result.exit_code)

    if aggregate_code == 0:
        print(f"[PASS] validación Literature_cases completa: {len(case_dirs)} caso(s)")
    return aggregate_code


if __name__ == "__main__":
    sys.exit(main())
