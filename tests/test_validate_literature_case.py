"""Tests para scripts/validate_literature_case.py."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts.validate_literature_case import (
    ContractError,
    discover_case_dirs,
    load_manifest,
    main,
    validate_case,
)


def _manifest_entry(path: str, payload: bytes, **extra: object) -> dict[str, object]:
    return {
        "path": path,
        "size_bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "immutable": True,
        **extra,
    }


def _write_case(
    parent: Path,
    name: str = "102 - Methanol_Water_Distillation",
    *,
    payload: bytes = b"fossee-source",
) -> Path:
    case_dir = parent / name
    case_dir.mkdir(parents=True)
    (case_dir / "source.dwxmz").write_bytes(payload)
    manifest = {"files": [_manifest_entry("source.dwxmz", payload)]}
    (case_dir / "source_manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )
    return case_dir


def _rewrite_manifest(case_dir: Path, document: object) -> None:
    (case_dir / "source_manifest.json").write_text(
        json.dumps(document), encoding="utf-8"
    )


def test_valid_case_defaults_expected_status_to_present(tmp_path: Path) -> None:
    case_dir = _write_case(tmp_path)

    result = validate_case(case_dir)

    assert result.exit_code == 0
    assert result.checked_files == 1
    assert not result.mismatches
    assert not result.contract_errors


@pytest.mark.parametrize("field", ["size_bytes", "sha256"])
def test_size_or_sha_mismatch_returns_one(tmp_path: Path, field: str) -> None:
    case_dir = _write_case(tmp_path)
    manifest = json.loads((case_dir / "source_manifest.json").read_text(encoding="utf-8"))
    manifest["files"][0][field] = 99 if field == "size_bytes" else "0" * 64
    _rewrite_manifest(case_dir, manifest)

    result = validate_case(case_dir)

    assert result.exit_code == 1
    assert result.mismatches
    assert not result.contract_errors


def test_missing_expected_file_returns_one(tmp_path: Path) -> None:
    case_dir = _write_case(tmp_path)
    (case_dir / "source.dwxmz").unlink()

    assert validate_case(case_dir).exit_code == 1


def test_expected_absent_passes_and_present_file_mismatches(tmp_path: Path) -> None:
    case_dir = tmp_path / "case"
    case_dir.mkdir()
    _rewrite_manifest(
        case_dir,
        {"files": [{"path": "not-published.bin", "expected_status": "ABSENT"}]},
    )
    assert validate_case(case_dir).exit_code == 0

    (case_dir / "not-published.bin").write_bytes(b"unexpected")
    assert validate_case(case_dir).exit_code == 1


@pytest.mark.parametrize(
    "unsafe_path",
    ["../outside.bin", "nested/../../outside.bin", "/absolute.bin", r"C:\outside.bin"],
)
def test_path_escape_or_absolute_path_is_contract_error(
    tmp_path: Path, unsafe_path: str
) -> None:
    case_dir = tmp_path / "case"
    case_dir.mkdir()
    _rewrite_manifest(case_dir, {"files": [_manifest_entry(unsafe_path, b"x")]})

    assert validate_case(case_dir).exit_code == 2


def test_case_insensitive_equivalent_paths_are_duplicates(tmp_path: Path) -> None:
    case_dir = tmp_path / "case"
    case_dir.mkdir()
    payload = b"x"
    _rewrite_manifest(
        case_dir,
        {
            "files": [
                _manifest_entry("Assets/Source.bin", payload),
                _manifest_entry(r"assets\source.bin", payload),
            ]
        },
    )

    result = validate_case(case_dir)

    assert result.exit_code == 2
    assert "duplicadas" in result.contract_errors[0]


def test_invalid_expected_status_is_contract_error(tmp_path: Path) -> None:
    case_dir = _write_case(tmp_path)
    manifest = json.loads((case_dir / "source_manifest.json").read_text(encoding="utf-8"))
    manifest["files"][0]["expected_status"] = "unknown"
    _rewrite_manifest(case_dir, manifest)

    assert validate_case(case_dir).exit_code == 2


def test_duplicate_json_key_is_contract_error(tmp_path: Path) -> None:
    case_dir = tmp_path / "case"
    case_dir.mkdir()
    (case_dir / "source_manifest.json").write_text(
        '{"files": [], "files": []}', encoding="utf-8"
    )

    with pytest.raises(ContractError, match="clave JSON duplicada"):
        load_manifest(case_dir / "source_manifest.json")


def test_corpus_comparison_is_byte_for_byte(tmp_path: Path) -> None:
    published_parent = tmp_path / "published"
    corpus_parent = tmp_path / "corpus"
    published = _write_case(published_parent, payload=b"same bytes")
    corpus = corpus_parent / "102"
    corpus.mkdir(parents=True)
    (corpus / "source.dwxmz").write_bytes(b"same bytes")

    assert validate_case(published, corpus).exit_code == 0

    (corpus / "source.dwxmz").write_bytes(b"other byte")
    result = validate_case(published, corpus)
    assert result.exit_code == 1
    assert any("byte a byte" in mismatch for mismatch in result.mismatches)


def test_root_mode_validates_all_cases_and_ignores_root_readme(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    literature_root = tmp_path / "Literature_cases"
    literature_root.mkdir()
    (literature_root / "README.md").write_text("# Índice\n", encoding="utf-8")
    _write_case(literature_root, "102 - Case")
    _write_case(literature_root, "103 - Case")

    assert main([str(literature_root)]) == 0
    output = capsys.readouterr().out
    assert "2 caso(s)" in output
    assert "README" not in output


def test_collection_mode_maps_cases_beneath_corpus_root(tmp_path: Path) -> None:
    literature_root = tmp_path / "Literature_cases"
    corpus_root = tmp_path / "corpus"
    for name in ("102 - Case", "103 - Case"):
        _write_case(literature_root, name, payload=name.encode())
        corpus_case = corpus_root / name
        corpus_case.mkdir(parents=True)
        (corpus_case / "source.dwxmz").write_bytes(name.encode())

    assert main([str(literature_root), "--corpus-case", str(corpus_root)]) == 0


def test_child_directory_without_manifest_is_contract_error(tmp_path: Path) -> None:
    literature_root = tmp_path / "Literature_cases"
    (literature_root / "102 - incomplete").mkdir(parents=True)

    with pytest.raises(ContractError, match="sin source_manifest.json"):
        discover_case_dirs(literature_root)
    assert main([str(literature_root)]) == 2


@pytest.mark.parametrize(
    "document",
    [
        {},
        {"files": []},
        {"files": "source.dwxmz"},
        {"files": [{"path": "source.dwxmz", "size_bytes": -1, "sha256": "0" * 64}]},
        {"files": [{"path": "source.dwxmz", "size_bytes": 1, "sha256": "bad"}]},
        {
            "files": [
                {
                    "path": "source.dwxmz",
                    "size_bytes": 1,
                    "sha256": "0" * 64,
                    "immutable": "yes",
                }
            ]
        },
    ],
)
def test_invalid_manifest_contract_returns_two(tmp_path: Path, document: object) -> None:
    case_dir = tmp_path / "case"
    case_dir.mkdir()
    _rewrite_manifest(case_dir, document)

    assert validate_case(case_dir).exit_code == 2
