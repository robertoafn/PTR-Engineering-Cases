from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = (
    ROOT
    / "cases"
    / "004_control_contaminacion_cruzada_validacion_cruzada"
    / "scripts"
)


def _load_script(filename: str):
    name = f"case004_{Path(filename).stem}"
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / filename)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def nrtl():
    return _load_script("crosscheck_nrtl_dechema.py")


@pytest.fixture(scope="module")
def vle():
    return _load_script("vle_comparison_dwsim_literature.py")


@pytest.fixture(scope="module")
def parity():
    return _load_script("parity_check_002.py")


@pytest.fixture(scope="module")
def sensitivity():
    return _load_script("sensitivity_hx301.py")


@pytest.fixture(scope="module")
def extraction():
    return _load_script("extract_saved_results.py")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _nrtl_parameter_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "source_id": "fixture-without-literature-claim",
                "model": "NRTL",
                "component_1": "methanol",
                "component_2": "water",
                "component_order": "1=methanol;2=water",
                "convention": "tau_ij=A_ij+B_ij/T_K",
                "temperature_unit": "K",
                "A_unit": "dimensionless",
                "B_unit": "K",
                "A12": 0.0,
                "A21": 0.0,
                "B12": 0.0,
                "B21": 0.0,
                "alpha12": 0.2,
                "alpha21": 0.2,
            }
        ]
    )


def test_nrtl_ideal_contract_returns_unity_and_passes(tmp_path: Path, nrtl) -> None:
    parameters = tmp_path / "parameters.csv"
    points = tmp_path / "dwsim.csv"
    output = tmp_path / "result.csv"
    _nrtl_parameter_frame().to_csv(parameters, index=False)
    pd.DataFrame(
        {
            "component_1": ["methanol"] * 3,
            "component_2": ["water"] * 3,
            "temperature_K": [300.0, 350.0, 400.0],
            "x_component_1": [0.0, 0.5, 1.0],
            "gamma_component_1_dwsim": [1.0, 1.0, 1.0],
            "gamma_component_2_dwsim": [1.0, 1.0, 1.0],
        }
    ).to_csv(points, index=False)

    code = nrtl.main(
        [
            "--parameters",
            str(parameters),
            "--dwsim-points",
            str(points),
            "--output",
            str(output),
        ]
    )

    assert code == 0
    result = pd.read_csv(output)
    assert result["status"].eq("PASS").all()
    assert result["gamma_component_1_calculated"].eq(1.0).all()
    assert result["gamma_component_2_calculated"].eq(1.0).all()


def test_nrtl_missing_input_is_not_run_and_does_not_write(
    tmp_path: Path, nrtl, capsys: pytest.CaptureFixture[str]
) -> None:
    output = tmp_path / "must_not_exist.csv"
    code = nrtl.main(
        [
            "--parameters",
            str(tmp_path / "missing_parameters.csv"),
            "--dwsim-points",
            str(tmp_path / "missing_points.csv"),
            "--output",
            str(output),
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    assert code == 2
    assert payload["status"] == "NOT_RUN"
    assert payload["output_written"] is False
    assert not output.exists()


def test_nrtl_rejects_output_equal_to_parameters_without_altering_input(
    tmp_path: Path, nrtl, capsys: pytest.CaptureFixture[str]
) -> None:
    parameters = tmp_path / "parameters.csv"
    _nrtl_parameter_frame().to_csv(parameters, index=False)
    before = _sha256(parameters)

    code = nrtl.main(
        [
            "--parameters",
            str(parameters),
            "--dwsim-points",
            str(tmp_path / "missing_points.csv"),
            "--output",
            str(parameters),
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    assert code == 2
    assert payload["status"] == "NOT_RUN"
    assert "colisiona con --output" in payload["message"]
    assert payload["output_written"] is False
    assert _sha256(parameters) == before


def test_nrtl_default_output_matches_validation_spec(nrtl) -> None:
    assert nrtl.DEFAULT_OUTPUT.name == "nrtl_activity_crosscheck_v01.csv"


def test_nrtl_rejects_implicit_component_order(tmp_path: Path, nrtl) -> None:
    parameters = tmp_path / "parameters.csv"
    frame = _nrtl_parameter_frame()
    frame.loc[0, "component_order"] = "methanol-water"
    frame.to_csv(parameters, index=False)
    with pytest.raises(nrtl.ContractError, match="component_order"):
        nrtl.read_parameter_contract(parameters)


def _vle_curve(source_id: str) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "source_id": [source_id] * 3,
            "component_1": ["methanol"] * 3,
            "component_2": ["water"] * 3,
            "temperature_K": [373.15, 355.15, 338.15],
            "pressure_Pa": [101325.0] * 3,
            "x_component_1_molfrac": [0.0, 0.5, 1.0],
            "y_component_1_molfrac": [0.0, 0.7, 1.0],
        }
    )


def test_vle_identical_curves_pass_without_extrapolation(tmp_path: Path, vle) -> None:
    literature = tmp_path / "literature.csv"
    dwsim = tmp_path / "dwsim.csv"
    output = tmp_path / "result.csv"
    _vle_curve("experimental-fixture").to_csv(literature, index=False)
    _vle_curve("dwsim-fixture").to_csv(dwsim, index=False)

    code = vle.main(
        [
            "--literature",
            str(literature),
            "--dwsim",
            str(dwsim),
            "--output",
            str(output),
        ]
    )

    assert code == 0
    result = pd.read_csv(output)
    assert result["status"].eq("PASS").all()
    assert result["max_abs_temperature_error_K"].abs().max() == pytest.approx(0.0)
    assert result["abs_x_error_molfrac"].abs().max() == pytest.approx(0.0)
    assert result["abs_y_error_molfrac"].abs().max() == pytest.approx(0.0)


def test_vle_missing_input_is_not_run_and_does_not_write(
    tmp_path: Path, vle, capsys: pytest.CaptureFixture[str]
) -> None:
    output = tmp_path / "must_not_exist.csv"
    code = vle.main(
        [
            "--literature",
            str(tmp_path / "missing_literature.csv"),
            "--dwsim",
            str(tmp_path / "missing_dwsim.csv"),
            "--output",
            str(output),
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    assert code == 2
    assert payload["status"] == "NOT_RUN"
    assert payload["output_written"] is False
    assert not output.exists()


def test_vle_rejects_output_equal_to_literature_without_altering_input(
    tmp_path: Path, vle, capsys: pytest.CaptureFixture[str]
) -> None:
    literature = tmp_path / "literature.csv"
    _vle_curve("experimental-fixture").to_csv(literature, index=False)
    before = _sha256(literature)

    code = vle.main(
        [
            "--literature",
            str(literature),
            "--dwsim",
            str(tmp_path / "missing_dwsim.csv"),
            "--output",
            str(literature),
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    assert code == 2
    assert payload["status"] == "NOT_RUN"
    assert "colisiona con --output" in payload["message"]
    assert payload["output_written"] is False
    assert _sha256(literature) == before


def test_vle_defaults_match_validation_spec(vle) -> None:
    args = vle.build_parser().parse_args([])
    assert vle.DEFAULT_OUTPUT.name == "vle_meoh_h2o_comparison_v01.csv"
    assert args.temperature_tolerance_K == pytest.approx(0.01)


@pytest.mark.parametrize(
    ("temperature_offset_k", "expected_status"),
    [(0.009, "PASS"), (0.011, "FAIL")],
)
def test_vle_temperature_tolerance_boundary(
    vle,
    temperature_offset_k: float,
    expected_status: str,
) -> None:
    literature = _vle_curve("experimental-fixture")
    dwsim = _vle_curve("dwsim-fixture")
    dwsim["temperature_K"] += temperature_offset_k

    result = vle.build_comparison(
        literature,
        dwsim,
        temperature_tolerance_k=0.01,
        composition_tolerance=0.01,
        pressure_tolerance_pa=100.0,
    )

    assert result["status"].eq(expected_status).all()


def test_vle_out_of_range_point_is_not_run(tmp_path: Path, vle) -> None:
    literature = _vle_curve("experimental-fixture")
    literature.loc[2, "x_component_1_molfrac"] = 1.0
    dwsim = _vle_curve("dwsim-fixture").iloc[:2].copy()
    with pytest.raises(vle.ContractError, match="no se extrapola"):
        vle.build_comparison(
            literature,
            dwsim,
            temperature_tolerance_k=1.0,
            composition_tolerance=0.01,
            pressure_tolerance_pa=100.0,
        )


def _parity_dataset() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "object_id": "MSTR-TEST",
                "temperature_K": 350.0,
                "pressure_Pa": 300000.0,
                "mass_flow_kg_s": 2.0,
                "specific_enthalpy_kJ_kg": -50.0,
                "energy_flow_kW": -100.0,
            }
        ]
    )


def test_parity_table_separates_state_and_energy_thresholds(parity) -> None:
    payload = {
        "objects": [
            {
                "object_id": "MSTR-TEST",
                "object_tag": "MSTR-TEST",
                "temperature_K": 350.0,
                "pressure_Pa": 300000.0,
                "mass_flow_kg_s": 2.0,
                "specific_enthalpy_kJ_kg": -50.0,
                "energy_flow_kW": -101.0,
            }
        ]
    }
    result = parity.build_parity_table(
        _parity_dataset(),
        payload,
        state_tolerance_percent=0.05,
        energy_tolerance_percent=0.05,
    )
    assert result.loc[result["scope"] == "state", "status"].eq("PASS").all()
    energy = result.loc[result["scope"] == "energy"].iloc[0]
    assert energy["relative_difference_percent"] == pytest.approx(1.0)
    assert energy["status"] == "FAIL"

    summary = parity.build_parity_summary(result)
    assert list(summary.columns) == [
        "object_id",
        "max_state_difference_percent",
        "max_energy_difference_percent",
        "state_tolerance_percent",
        "energy_tolerance_percent",
        "state_status",
        "energy_status",
        "failed_metrics",
        "overall_status",
    ]
    assert summary.iloc[0]["failed_metrics"] == "energy_flow_kW"
    assert summary.iloc[0]["overall_status"] == "FAIL"


def test_parity_missing_runner_is_not_run_and_does_not_write(
    tmp_path: Path, parity, capsys: pytest.CaptureFixture[str]
) -> None:
    dataset = tmp_path / "dataset.csv"
    simulation = tmp_path / "simulation.dwxmz"
    output = tmp_path / "must_not_exist.csv"
    _parity_dataset().to_csv(dataset, index=False)
    simulation.write_bytes(b"source-preservation-fixture")

    code = parity.main(
        [
            "--dataset",
            str(dataset),
            "--simulation",
            str(simulation),
            "--runner",
            str(tmp_path / "missing_runner.exe"),
            "--output",
            str(output),
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    assert code == 2
    assert payload["status"] == "NOT_RUN"
    assert payload["output_written"] is False
    assert not output.exists()


def test_parity_runner_failure_with_intact_source_is_not_integrity_failure(
    tmp_path: Path, parity, monkeypatch: pytest.MonkeyPatch
) -> None:
    runner = tmp_path / "runner.exe"
    simulation = tmp_path / "simulation.dwxmz"
    runner.write_bytes(b"runner-fixture")
    simulation.write_bytes(b"immutable-simulation")
    before = _sha256(simulation)

    completed = SimpleNamespace(
        stdout=json.dumps(
            {
                "solved": False,
                "errors": [{"code": "DwsimHomeNotFound"}],
            }
        ),
        stderr="",
        returncode=1,
    )
    monkeypatch.setattr(parity.subprocess, "run", lambda *args, **kwargs: completed)

    with pytest.raises(parity.ExecutionUnavailable, match="sin una solución"):
        parity.run_dwsim(
            runner=runner,
            simulation=simulation,
            object_ids=["MSTR-TEST"],
            required_version="9.0.5",
            timeout_seconds=10.0,
            dwsim_home=None,
        )

    assert _sha256(simulation) == before


def test_parity_rejects_output_equal_to_simulation_without_altering_source(
    tmp_path: Path, parity, capsys: pytest.CaptureFixture[str]
) -> None:
    dataset = tmp_path / "dataset.csv"
    simulation = tmp_path / "simulation.dwxmz"
    _parity_dataset().to_csv(dataset, index=False)
    simulation.write_bytes(b"immutable-parity-source")
    before = _sha256(simulation)

    code = parity.main(
        [
            "--dataset",
            str(dataset),
            "--simulation",
            str(simulation),
            "--runner",
            str(tmp_path / "missing_runner.exe"),
            "--output",
            str(simulation),
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    assert code == 2
    assert payload["status"] == "NOT_RUN"
    assert "colisiona con --simulation" in payload["message"]
    assert payload["output_written"] is False
    assert _sha256(simulation) == before


def test_sensitivity_rejects_output_equal_to_simulation_without_running_dwsim(
    tmp_path: Path, sensitivity
) -> None:
    simulation = tmp_path / "simulation.dwxmz"
    simulation.write_bytes(b"immutable-sensitivity-source")
    before = _sha256(simulation)

    with pytest.raises(sensitivity.SensitivityError, match="--simulation"):
        sensitivity.main(
            [
                "--simulation",
                str(simulation),
                "--runner",
                str(tmp_path / "missing_runner.exe"),
                "--output",
                str(simulation),
            ]
        )

    assert _sha256(simulation) == before


def test_extraction_rejects_output_equal_to_simulation_without_altering_source(
    tmp_path: Path, extraction
) -> None:
    simulation = tmp_path / "simulation.dwxmz"
    equipment_output = tmp_path / "equipment.csv"
    simulation.write_bytes(b"immutable-extraction-source")
    before = _sha256(simulation)

    with pytest.raises(ValueError, match="--simulation.*--process-output"):
        extraction.main(
            [
                "--simulation",
                str(simulation),
                "--process-output",
                str(simulation),
                "--equipment-output",
                str(equipment_output),
            ]
        )

    assert _sha256(simulation) == before
    assert not equipment_output.exists()


def test_extraction_rejects_colliding_outputs_before_writing(
    tmp_path: Path, extraction
) -> None:
    simulation = tmp_path / "simulation.dwxmz"
    shared_output = tmp_path / "shared.csv"
    simulation.write_bytes(b"immutable-extraction-source")
    before = _sha256(simulation)

    with pytest.raises(ValueError, match="--process-output.*--equipment-output"):
        extraction.main(
            [
                "--simulation",
                str(simulation),
                "--process-output",
                str(shared_output),
                "--equipment-output",
                str(shared_output),
            ]
        )

    assert _sha256(simulation) == before
    assert not shared_output.exists()
