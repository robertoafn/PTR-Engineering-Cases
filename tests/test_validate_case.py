"""Pruebas del motor declarativo de validación PTR."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest
import yaml

from scripts import validate_case as engine


def _criterion(
    criterion_id: str,
    criterion_type: str,
    **extra: object,
) -> dict[str, object]:
    return {
        "id": criterion_id,
        "title": criterion_id.replace("_", " "),
        "type": criterion_type,
        "scope": "numerical",
        "blocking": True,
        "required": True,
        **extra,
    }


def _make_case(
    tmp_path: Path,
    rows: list[dict[str, object]],
    criteria: list[dict[str, object]],
    *,
    outputs: list[dict[str, object]] | None = None,
) -> Path:
    case_dir = tmp_path / "901_caso_prueba"
    data_dir = case_dir / "data"
    data_dir.mkdir(parents=True)
    pd.DataFrame(rows).to_csv(data_dir / "process.csv", index=False)
    metadata = {
        "case_id": case_dir.name,
        "version": "0.1.0",
        "status": "review",
        "outputs": outputs or [],
    }
    spec = {
        "schema_version": "1.0.0",
        "case_id": case_dir.name,
        "datasets": {
            "process": {
                "path": "data/process.csv",
                "id_column": "object_id",
            }
        },
        "criteria": criteria,
    }
    (case_dir / "metadata.yaml").write_text(
        yaml.safe_dump(metadata, sort_keys=False), encoding="utf-8"
    )
    (case_dir / "validation_spec.yaml").write_text(
        yaml.safe_dump(spec, sort_keys=False), encoding="utf-8"
    )
    return case_dir


def _threshold(
    value: float,
    *,
    operator: str = "<=",
    unit: str = "%",
) -> dict[str, object]:
    return {"operator": operator, "value": value, "unit": unit}


def test_global_mass_balance_excludes_internal_and_accepts_multiple_outlets(
    tmp_path: Path,
) -> None:
    case = _make_case(
        tmp_path,
        [
            {"object_id": "IN", "mass_flow_kg_s": 10.0},
            {"object_id": "INTERNAL", "mass_flow_kg_s": 10.0},
            {"object_id": "OUT_A", "mass_flow_kg_s": 4.0},
            {"object_id": "OUT_B", "mass_flow_kg_s": 6.0},
        ],
        [
            _criterion(
                "mass",
                "global_mass_balance",
                dataset="process",
                value_column="mass_flow_kg_s",
                inlet_ids=["IN"],
                outlet_ids=["OUT_A", "OUT_B"],
                threshold=_threshold(0.5),
            )
        ],
    )

    result = engine.validate_case(case, source="dataset")

    assert result["overall_status"] == "PASS"
    assert result["criteria"][0]["result"]["value"] == pytest.approx(0.0)


def test_two_independent_side_mass_balances(tmp_path: Path) -> None:
    rows = [
        {"object_id": "HOT_IN", "mass_flow_kg_s": 8.0},
        {"object_id": "HOT_OUT", "mass_flow_kg_s": 8.0},
        {"object_id": "COLD_IN", "mass_flow_kg_s": 5.0},
        {"object_id": "COLD_OUT", "mass_flow_kg_s": 5.0},
    ]
    criteria = [
        _criterion(
            "hot_side",
            "side_mass_balance",
            dataset="process",
            value_column="mass_flow_kg_s",
            inlet_ids=["HOT_IN"],
            outlet_ids=["HOT_OUT"],
            threshold=_threshold(0.01),
        ),
        _criterion(
            "cold_side",
            "side_mass_balance",
            dataset="process",
            value_column="mass_flow_kg_s",
            inlet_ids=["COLD_IN"],
            outlet_ids=["COLD_OUT"],
            threshold=_threshold(0.01),
        ),
    ]
    result = engine.validate_case(_make_case(tmp_path, rows, criteria), source="dataset")

    assert [item["status"] for item in result["criteria"]] == ["PASS", "PASS"]


def test_energy_balance_honours_term_signs(tmp_path: Path) -> None:
    case = _make_case(
        tmp_path,
        [
            {"object_id": "FEED", "energy_flow_kW": 100.0},
            {"object_id": "PRODUCT", "energy_flow_kW": 40.0},
            {"object_id": "DUTY", "energy_flow_kW": 60.0},
        ],
        [
            _criterion(
                "energy",
                "stream_energy_balance",
                terms=[
                    {
                        "dataset": "process",
                        "column": "energy_flow_kW",
                        "ids": ["FEED"],
                        "factor": 1.0,
                    },
                    {
                        "dataset": "process",
                        "column": "energy_flow_kW",
                        "ids": ["PRODUCT"],
                        "factor": -1.0,
                    },
                    {
                        "dataset": "process",
                        "column": "energy_flow_kW",
                        "ids": ["DUTY"],
                        "factor": -1.0,
                    },
                ],
                normalization="max_side",
                threshold=_threshold(0.1),
            )
        ],
    )

    criterion = engine.validate_case(case, source="dataset")["criteria"][0]

    assert criterion["status"] == "PASS"
    assert criterion["result"]["value"] == pytest.approx(0.0)


@pytest.mark.parametrize(
    ("outlet", "expected"),
    [(-99.0, "PASS"), (-98.999, "FAIL")],
)
def test_isenthalpic_threshold_is_exact(
    tmp_path: Path, outlet: float, expected: str
) -> None:
    case = _make_case(
        tmp_path,
        [
            {"object_id": "IN", "h": -100.0},
            {"object_id": "OUT", "h": outlet},
        ],
        [
            _criterion(
                "isoenthalpic",
                "isenthalpic",
                left={"dataset": "process", "column": "h", "ids": ["IN"]},
                right={"dataset": "process", "column": "h", "ids": ["OUT"]},
                calculation="relative_difference_percent",
                threshold=_threshold(1.0),
            )
        ],
    )

    assert engine.validate_case(case, source="dataset")["criteria"][0]["status"] == expected


def test_missing_column_is_n_a_and_strict_fails(tmp_path: Path) -> None:
    case = _make_case(
        tmp_path,
        [{"object_id": "IN", "mass_flow_kg_s": 1.0}],
        [
            _criterion(
                "energy",
                "reported_metric",
                value={
                    "dataset": "process",
                    "column": "specific_enthalpy_kJ_kg",
                    "ids": ["IN"],
                },
                threshold=_threshold(1.0, unit="kJ/kg"),
                unavailable_status="N_A",
            )
        ],
    )

    result = engine.validate_case(case, source="dataset")

    assert result["criteria"][0]["status"] == "N_A"
    assert result["overall_status"] == "CONDITIONAL"
    assert engine.result_exit_code(result) == 0
    assert engine.result_exit_code(result, strict=True) == 1


def test_reported_metric_from_metadata(tmp_path: Path) -> None:
    case = _make_case(
        tmp_path,
        [{"object_id": "IN", "x": 1.0}],
        [
            _criterion(
                "reported",
                "reported_metric",
                value={"metadata_output": "residuo"},
                threshold=_threshold(0.5),
            )
        ],
        outputs=[{"name": "residuo", "value": 0.25}],
    )

    criterion = engine.validate_case(case, source="dataset")["criteria"][0]

    assert criterion["status"] == "PASS"
    assert criterion["evidence_source"] == "reported_metric"


def test_pressure_margin_can_be_not_demonstrated(tmp_path: Path) -> None:
    case = _make_case(
        tmp_path,
        [
            {"object_id": "CLEAN", "pressure_Pa": 300000.0},
            {"object_id": "DIRTY", "pressure_Pa": 300000.0},
        ],
        [
            _criterion(
                "pressure",
                "pressure_margin",
                scope="safety",
                blocking=False,
                left={
                    "dataset": "process",
                    "column": "pressure_Pa",
                    "ids": ["CLEAN"],
                },
                right={
                    "dataset": "process",
                    "column": "pressure_Pa",
                    "ids": ["DIRTY"],
                },
                calculation="absolute_difference",
                threshold=_threshold(0.0, operator=">", unit="Pa"),
                failure_status="NOT_DEMONSTRATED",
            )
        ],
    )

    result = engine.validate_case(case, source="dataset")

    assert result["criteria"][0]["status"] == "NOT_DEMONSTRATED"
    assert result["overall_status"] == "CONDITIONAL"


def test_invalid_checksum_is_blocking_failure(tmp_path: Path) -> None:
    criterion = _criterion(
        "checksums",
        "existing_validators",
        scope="data_quality",
        validators=["checksums"],
        threshold=_threshold(0.0, unit="errores"),
    )
    case = _make_case(
        tmp_path,
        [{"object_id": "IN", "mass_flow_kg_s": 1.0}],
        [criterion],
    )
    (case / "provenance.json").write_text(
        json.dumps(
            {
                "entities": [
                    {
                        "path": "data/process.csv",
                        "checksum_sha256": "0" * 64,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    result = engine.validate_case(case, source="dataset")

    assert result["criteria"][0]["status"] == "FAIL"
    assert engine.result_exit_code(result) == 1


def test_missing_declared_unit_is_detected_by_existing_table_validator(
    tmp_path: Path,
) -> None:
    case = _make_case(
        tmp_path,
        [{"object_id": "IN", "mass_flow_kg_s": 1.0}],
        [
            _criterion(
                "units",
                "existing_validators",
                scope="data_quality",
                validators=["tables"],
                threshold=_threshold(0.0, unit="errores"),
            )
        ],
    )
    csv_path = case / "data" / "process.csv"
    sidecar = {
        "dataset_id": "process_v01",
        "case_id": case.name,
        "source_type": "simulated",
        "variables": [
            {
                "symbol": "object_id",
                "column": "object_id",
                "name": "Identificador",
                "unit": "dimensionless",
                "type": "string",
            },
            {
                "symbol": "m_dot",
                "column": "mass_flow_kg_s",
                "name": "Caudal",
                "type": "float",
            },
        ],
        "created_at": "2026-07-25T12:00:00Z",
        "version": "0.1.0",
        "checksum_sha256": engine.sha256(csv_path),
    }
    (case / "data" / "process.meta.yaml").write_text(
        yaml.safe_dump(sidecar, sort_keys=False), encoding="utf-8"
    )

    criterion = engine.validate_case(case, source="dataset")["criteria"][0]

    assert criterion["status"] == "FAIL"
    assert "sidecar schema" in criterion["message"]


def test_incomplete_configuration_returns_failure(tmp_path: Path) -> None:
    case = tmp_path / "902_incompleto"
    case.mkdir()
    (case / "metadata.yaml").write_text(
        "case_id: 902_incompleto\nversion: 0.1.0\nstatus: draft\n",
        encoding="utf-8",
    )
    (case / "validation_spec.yaml").write_text(
        "schema_version: 1.0.0\ncase_id: 902_incompleto\n",
        encoding="utf-8",
    )

    result = engine.validate_case(case, source="dataset")

    assert result["overall_status"] == "FAIL"
    assert engine.result_exit_code(result) == 1
    engine.validate_result_document(result)


def test_auto_falls_back_but_dwsim_mode_fails_without_runner(tmp_path: Path) -> None:
    criterion = _criterion(
        "mass",
        "global_mass_balance",
        dataset="process",
        inlet_ids=["IN"],
        outlet_ids=["OUT"],
        threshold=_threshold(0.5),
    )
    case = _make_case(
        tmp_path,
        [
            {"object_id": "IN", "mass_flow_kg_s": 1.0},
            {"object_id": "OUT", "mass_flow_kg_s": 1.0},
        ],
        [criterion],
    )
    spec = yaml.safe_load((case / "validation_spec.yaml").read_text(encoding="utf-8"))
    spec["dwsim"] = {
        "file": "simulations/case.dwxmz",
        "required_version": "9.0.5",
    }
    (case / "validation_spec.yaml").write_text(
        yaml.safe_dump(spec, sort_keys=False), encoding="utf-8"
    )
    missing_runner = tmp_path / "missing.exe"

    fallback = engine.validate_case(
        case, source="auto", runner_path=missing_runner
    )
    required = engine.validate_case(
        case, source="dwsim", runner_path=missing_runner
    )

    assert fallback["actual_source"] == "exported_dataset"
    assert "fallback" in fallback["source_message"]
    assert fallback["overall_status"] == "PASS"
    assert required["actual_source"] == "not_available"
    assert required["overall_status"] == "FAIL"


def test_dwsim_objects_merge_only_matching_rows_and_aliases() -> None:
    frames = {
        "process": pd.DataFrame(
            [
                {"object_id": "A", "mass_flow_kg_s": 1.0},
                {"object_id": "B", "mass_flow_kg_s": 2.0},
            ]
        ),
        "chromatography": pd.DataFrame(
            [{"sample_id": "S-1", "area": 99.0}]
        ),
    }
    spec = {
        "datasets": {
            "process": {"id_column": "object_id"},
            "chromatography": {"id_column": "sample_id"},
        },
        "dwsim": {"object_map": {"A": "DWSIM-A"}},
        "criteria": [
            {
                "terms": [
                    {
                        "dataset": "process",
                        "column": "duty_kW",
                        "ids": ["SEP"],
                    }
                ]
            }
        ],
    }
    payload = {
        "objects": [
            {
                "object_id": "GUID-A",
                "object_tag": "DWSIM-A",
                "object_type": "Material Stream",
                "mass_flow_kg_s": 3.0,
                "temperature_K": 300.0,
            },
            {
                "id": "EXTRA",
                "type": "Material Stream",
                "properties": {"mass_flow_kg_s": 4.0},
            },
            {
                "object_tag": "SEP",
                "object_type": "Vessel",
                "duty_kW": -10.0,
            },
        ]
    }

    engine._merge_dwsim_evidence(frames, spec, payload)

    assert len(frames["process"]) == 3
    assert frames["process"].set_index("object_id").loc["A", "mass_flow_kg_s"] == 3.0
    assert (
        frames["process"].set_index("object_id").loc["A", "mass_flow_kg_s_dataset"]
        == 1.0
    )
    assert frames["process"].set_index("object_id").loc["SEP", "duty_kW"] == -10.0
    assert "EXTRA" not in set(frames["process"]["object_id"])
    assert list(frames["chromatography"]["sample_id"]) == ["S-1"]


def test_api_dataset_consistency_reports_maximum_and_is_not_run_without_api(
    tmp_path: Path,
) -> None:
    criterion = _criterion(
        "api_consistency",
        "api_dataset_consistency",
        scope="data_quality",
        blocking=True,
        required=False,
        dataset="process",
        ids=["A"],
        columns=[
            {
                "dataset_column": "temperature_K",
                "api_column": "temperature_K",
            }
        ],
        threshold=_threshold(0.5),
        unavailable_status="NOT_RUN",
    )
    case = _make_case(
        tmp_path,
        [{"object_id": "A", "temperature_K": 300.0}],
        [criterion],
    )
    dataset_result = engine.validate_case(case, source="dataset")
    frames, _ = engine.load_datasets(
        case,
        {
            "datasets": {
                "process": {
                    "path": "data/process.csv",
                    "id_column": "object_id",
                }
            }
        },
    )
    spec, metadata = engine.load_spec(case)
    engine._merge_dwsim_evidence(
        frames,
        spec,
        {
            "objects": [
                {
                    "object_tag": "A",
                    "object_type": "MaterialStream",
                    "temperature_K": 303.0,
                }
            ]
        },
    )
    api_result = engine.evaluate_criterion(
        criterion,
        case_dir=case,
        frames=frames,
        spec=spec,
        metadata=metadata,
        actual_source="dwsim_api",
    )

    assert dataset_result["criteria"][0]["status"] == "NOT_RUN"
    assert dataset_result["overall_status"] == "PASS"
    assert api_result["result"]["value"] == pytest.approx(1.0)
    assert api_result["status"] == "FAIL"
    assert engine._overall_status([api_result]) == "FAIL"
    assert "A temperature_K↔temperature_K" in api_result["message"]


def test_serialisation_is_stable_and_validates_schema(tmp_path: Path) -> None:
    case = _make_case(
        tmp_path,
        [
            {"object_id": "IN", "mass_flow_kg_s": 1.0},
            {"object_id": "OUT", "mass_flow_kg_s": 1.0},
        ],
        [
            _criterion(
                "mass",
                "global_mass_balance",
                dataset="process",
                inlet_ids=["IN"],
                outlet_ids=["OUT"],
                threshold=_threshold(0.5),
            )
        ],
    )
    result = engine.validate_case(
        case,
        source="dataset",
        generated_at_utc="2026-07-25T12:00:00Z",
    )

    first = engine.serialise_result(result)
    second = engine.serialise_result(result)

    assert first == second
    assert json.loads(first)["case_id"] == "901_caso_prueba"


def test_write_artifacts_preserves_narrative_and_replaces_only_section(
    tmp_path: Path,
) -> None:
    case = _make_case(
        tmp_path,
        [{"object_id": "A", "x": 1.0}],
        [
            _criterion(
                "range",
                "range",
                value={"dataset": "process", "column": "x", "ids": ["A"]},
                minimum=0.0,
                maximum=2.0,
            )
        ],
    )
    report = case / "validation_report.md"
    report.write_text("# Narrativa\n\nTexto técnico conservado.\n", encoding="utf-8")
    result = engine.validate_case(case, source="dataset")

    engine.write_artifacts(case, result)
    first = report.read_text(encoding="utf-8")
    engine.write_artifacts(case, result)
    second = report.read_text(encoding="utf-8")

    assert "Texto técnico conservado." in second
    assert second.count(engine.AUTO_START) == 1
    assert first == second
    assert (case / "validation_results.json").is_file()
