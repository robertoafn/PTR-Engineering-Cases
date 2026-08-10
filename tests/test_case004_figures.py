from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

import pandas as pd
import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = (
    ROOT
    / "cases"
    / "004_control_contaminacion_cruzada_validacion_cruzada"
)


def _load_module():
    path = CASE_DIR / "scripts" / "generate_figures.py"
    spec = importlib.util.spec_from_file_location("case004_generate_figures", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def figures():
    return _load_module()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_nominal_values_come_from_csv(figures) -> None:
    nominal = figures.load_nominal(
        CASE_DIR / "data" / "process_results_v01.csv",
        CASE_DIR / "data" / "processed" / "hx301_equipment_results_v01.csv",
    )

    assert nominal["hot_in_temperature_K"] == pytest.approx(406.649349770717)
    assert nominal["cold_in_pressure_Pa"] == pytest.approx(350000.0)
    assert nominal["overall_coefficient_W_m2_K"] == pytest.approx(1000.0)
    assert nominal["area_m2"] == pytest.approx(13.0)
    assert nominal["pressure_margin_inlet_Pa"] == pytest.approx(50000.0)


def test_pressure_summary_is_derived_from_sensitivity_csv(
    tmp_path: Path, figures
) -> None:
    source = CASE_DIR / "data" / "processed" / "hx301_sensitivity_v01.csv"
    frame = pd.read_csv(source)
    frame["clean_to_contaminated_deltaP_Pa"] = 42000.0
    changed = tmp_path / "sensitivity.csv"
    frame.to_csv(changed, index=False)

    rows = figures.load_sensitivity(changed)

    assert figures.pressure_margin_summary(rows) == (
        "ΔP_limpio−contaminado = +42 kPa"
    )


def test_collision_is_rejected_before_any_figure_write(
    tmp_path: Path, figures
) -> None:
    protected = tmp_path / "fig_004_01_pfd_hx301_instrumentado.png"
    protected.write_bytes(b"protected-input")
    before = _sha256(protected)

    with pytest.raises(ValueError, match="colisionan"):
        figures.reject_path_collisions(
            {
                "--process": tmp_path / "process.csv",
                "--equipment": tmp_path / "equipment.csv",
                "--sensitivity": protected,
            },
            {
                "figura PFD": protected,
                "figura sensibilidad": (
                    tmp_path / "fig_004_02_sensibilidad_u_q.png"
                ),
            },
        )

    assert _sha256(protected) == before


def test_full_generation_uses_versioned_inputs(
    tmp_path: Path, figures
) -> None:
    sensitivity = CASE_DIR / "data" / "processed" / "hx301_sensitivity_v01.csv"
    code = figures.main(
        [
            "--process",
            str(CASE_DIR / "data" / "process_results_v01.csv"),
            "--equipment",
            str(CASE_DIR / "data" / "processed" / "hx301_equipment_results_v01.csv"),
            "--sensitivity",
            str(sensitivity),
            "--output-dir",
            str(tmp_path),
        ]
    )

    assert code == 0
    for name in (
        "fig_004_01_pfd_hx301_instrumentado.png",
        "fig_004_02_sensibilidad_u_q.png",
    ):
        image_path = tmp_path / name
        assert image_path.is_file()
        with Image.open(image_path) as generated:
            assert generated.info["Source"].startswith("PTR Case 004")
