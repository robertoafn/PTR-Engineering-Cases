"""Valida el contrato mínimo e inmutable de SimulationRun."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "simulation_run.schema.json"
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "simulation_run_valid.json"
REPOSITORY_RUN_PATHS = sorted(
    (ROOT / "Literature_cases").glob("**/runs/*/simulation_run.json")
)

SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
VALID_RUN = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())


def validation_messages(instance: dict[str, object]) -> list[str]:
    """Devuelve errores ordenados para que los fallos sean diagnosticables."""
    return [
        error.message
        for error in sorted(VALIDATOR.iter_errors(instance), key=lambda item: list(item.path))
    ]


def sha256(path: Path) -> str:
    """Calcula SHA-256 sin cargar artefactos completos en memoria."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def make_saved_state_inspection() -> dict[str, object]:
    """Deriva un ejemplo válido de inspección sin afirmar que hubo recálculo."""
    instance = deepcopy(VALID_RUN)
    instance["run_type"] = "inspection"
    instance["version_role"] = "source_baseline"
    instance["software"]["release_channel"] = "unknown"
    instance["artifacts"] = [
        {
            "artifact_id": "artifact:999_source",
            "path": "Literature_cases/999_example/source.dwxmz",
            "role": "source_simulation",
            "sha256": "4" * 64,
            "immutable": True,
        }
    ]
    instance["execution"] = {
        "mode": "saved_state_inspection",
        "recalculated": False,
        "clean_start": False,
        "convergence_status": "saved_state_only",
    }
    instance["evidence"] = {
        "evidence_mode": "documentary",
        "data_origin": "literature",
        "source_ids": ["source:example_catalog_record"],
    }
    instance["provenance"]["used_artifact_ids"] = ["artifact:999_source"]
    instance["provenance"]["generated_artifact_ids"] = []
    return instance


def test_schema_is_valid_draft_2020_12() -> None:
    Draft202012Validator.check_schema(SCHEMA)


def test_target_reproducible_fixture_is_valid() -> None:
    assert validation_messages(VALID_RUN) == []


def test_saved_state_inspection_is_valid_when_explicit() -> None:
    assert validation_messages(make_saved_state_inspection()) == []


def test_repository_contains_a_canonical_simulation_run() -> None:
    assert REPOSITORY_RUN_PATHS


@pytest.mark.parametrize("manifest_path", REPOSITORY_RUN_PATHS)
def test_repository_simulation_runs_are_valid_and_hashes_resolve(
    manifest_path: Path,
) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert validation_messages(manifest) == []

    artifact_ids = {
        artifact["artifact_id"] for artifact in manifest["artifacts"]
    }
    assert set(manifest["provenance"]["used_artifact_ids"]) <= artifact_ids
    assert set(manifest["provenance"]["generated_artifact_ids"]) <= artifact_ids

    for artifact in manifest["artifacts"]:
        artifact_path = ROOT / artifact["path"]
        assert artifact_path.is_file(), artifact["path"]
        assert sha256(artifact_path) == artifact["sha256"]


def test_saved_state_inspection_rejects_claimed_recalculation() -> None:
    instance = make_saved_state_inspection()
    instance["execution"]["recalculated"] = True

    assert validation_messages(instance)


@pytest.mark.parametrize(
    ("section", "field", "value"),
    [
        ("software", "release_channel", "release_candidate"),
        ("execution", "clean_start", False),
        ("execution", "convergence_status", "reported_success"),
    ],
)
def test_target_reproducible_enforces_promotion_gate(
    section: str,
    field: str,
    value: object,
) -> None:
    instance = deepcopy(VALID_RUN)
    instance[section][field] = value

    assert validation_messages(instance)


def test_evidence_mode_and_data_origin_cannot_be_collapsed() -> None:
    instance = deepcopy(VALID_RUN)
    del instance["evidence"]["data_origin"]
    instance["evidence"]["source_type"] = "simulated"

    assert validation_messages(instance)


@pytest.mark.parametrize(
    "path",
    [
        r"C:\PTR-DWSIM-WORK\model.dwxmz",
        "../model.dwxmz",
        "/tmp/model.dwxmz",
        "https://example.com/model.dwxmz",
    ],
)
def test_artifact_path_must_be_repository_relative(path: str) -> None:
    instance = deepcopy(VALID_RUN)
    instance["artifacts"][0]["path"] = path

    assert validation_messages(instance)


def test_artifact_requires_lowercase_sha256_and_immutability() -> None:
    instance = deepcopy(VALID_RUN)
    instance["artifacts"][0]["sha256"] = "A" * 64
    instance["artifacts"][0]["immutable"] = False

    assert validation_messages(instance)
