"""Tests para scripts/validate_metadata.py."""
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "case_metadata.schema.json"
TEMPLATE = ROOT / "templates" / "case_template" / "metadata.yaml"


def _validator() -> Draft202012Validator:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    return Draft202012Validator(schema)


def test_template_metadata_structure_loadable() -> None:
    """La plantilla canónica debe parsear como YAML válido y tener los campos
    obligatorios declarados (aun con valores vacíos)."""
    data = yaml.safe_load(TEMPLATE.read_text(encoding="utf-8"))
    required_keys = {
        "case_id", "title", "phenomenon", "objective", "authors",
        "created_at", "version", "license_code", "license_docs",
        "software_stack", "inputs", "outputs", "qc_rules",
        "validation", "traceability", "si_units", "status",
    }
    assert required_keys.issubset(set(data.keys()))


def test_invalid_metadata_missing_required_fields_fails() -> None:
    """Quitar un campo obligatorio debe producir error de validación."""
    data = yaml.safe_load(TEMPLATE.read_text(encoding="utf-8"))
    del data["case_id"]
    errors = list(_validator().iter_errors(data))
    assert len(errors) >= 1
