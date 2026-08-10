from __future__ import annotations

import sys
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
MODULE_DIR = ROOT / "dashboards" / "streamlit"
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

from data_model import (  # noqa: E402
    criteria_frame,
    discover_case_dirs,
    load_all_cases,
    load_catalog,
    material_streams,
    portfolio_frame,
)
from science_model import (  # noqa: E402
    case_001_analysis,
    case_002_analysis,
    case_002_chromatogram_frame,
    case_002_gc_analysis,
    case_003_analysis,
    case_004_analysis,
    case_004_sensitivity_frame,
)


def _case(case_id: str):
    return next(item for item in load_all_cases(ROOT) if item.case_id == case_id)


def test_dashboard_discovers_the_four_implemented_cases() -> None:
    discovered = discover_case_dirs(ROOT)
    assert [path.name[:3] for path in discovered] == ["001", "002", "003", "004"]


def test_catalog_covers_the_scientific_narrative_and_evidence_links() -> None:
    cases = load_all_cases(ROOT)
    catalog = load_catalog(ROOT)
    assert catalog["schema_version"] == "2.0"
    assert set(catalog["cases"]) == {"001", "002", "003", "004"}
    assert catalog["proposals"]["005"]["status"] == "proposed"
    assert catalog["proposals"]["005"]["depends_on"] == "004"

    required_case_fields = {
        "scientific_question",
        "summary",
        "learning_outcomes",
        "figure_guide",
        "methods",
        "conclusion",
        "limitations",
    }
    required_phenomenon_fields = {
        "question",
        "explanation",
        "equation_latex",
        "data_reading",
        "engineering_meaning",
        "limitation",
    }
    for case in cases:
        criterion_ids = {item["id"] for item in case.validation["criteria"]}
        assert required_case_fields.issubset(case.catalog)
        assert case.catalog["learning_outcomes"]
        assert case.catalog["figure_guide"]
        assert case.catalog["methods"]
        phenomena = case.catalog["phenomena"]
        assert phenomena
        for phenomenon in phenomena:
            assert required_phenomenon_fields.issubset(phenomenon)
            assert set(phenomenon["evidence_criteria"]).issubset(criterion_ids)


def test_case_001_explains_mechanical_and_thermal_energy_scales() -> None:
    values = case_001_analysis(_case("001"))
    assert values["mass_flow_kg_s"] == pytest.approx(10.0)
    assert values["pressure_rise_kpa"] == pytest.approx(300.0)
    assert values["pump_efficiency"] == pytest.approx(0.75, rel=5e-3)
    assert values["temperature_rise_k"] == pytest.approx(39.9693, rel=1e-5)
    assert values["heater_duty_kw"] / values["pump_power_kw"] == pytest.approx(
        415.85, rel=1e-3
    )
    assert values["mass_residual_kg_s"] == pytest.approx(0.0, abs=1e-12)


def test_case_002_explains_flash_partition_and_chromatography() -> None:
    case = _case("002")
    values = case_002_analysis(case)
    gc, standards, samples = case_002_gc_analysis(case)
    signals = case_002_chromatogram_frame(case)

    assert values["pressure_drop_kpa"] == pytest.approx(900.0)
    assert values["temperature_drop_k"] == pytest.approx(46.4972, rel=1e-5)
    assert values["enthalpy_change_kj_kg"] == pytest.approx(0.0, abs=1e-5)
    assert 100.0 * values["vapor_mass_yield"] == pytest.approx(10.48878)
    assert 100.0 * values["methanol_recovery_vapor"] == pytest.approx(42.7935)
    assert values["methanol_enrichment_vapor_liquid"] == pytest.approx(
        6.38398, rel=1e-5
    )
    assert gc["r_squared"] == pytest.approx(0.99997113, rel=1e-7)
    assert gc["duplicate_rpd_percent"] == pytest.approx(2.4748225, rel=1e-7)
    assert len(standards) >= 3
    assert len(samples) >= 3
    assert set(signals["Muestra"]) == {
        "Blanco",
        "Alimentación",
        "Vapor condensado",
        "Vapor duplicado",
        "Líquido residual",
    }
    assert signals["time_s"].between(124.0, 133.0).any()


def test_case_003_explains_heat_exchange_and_hydraulic_limit() -> None:
    values = case_003_analysis(_case("003"))
    assert values["q_hot_kw"] == pytest.approx(1063.393056, rel=1e-8)
    assert values["q_cold_kw"] == pytest.approx(1063.4, rel=1e-8)
    assert values["energy_residual_kw"] == pytest.approx(-0.006944, abs=1e-6)
    assert values["hot_temperature_drop_k"] == pytest.approx(22.462, rel=1e-6)
    assert values["cold_temperature_rise_k"] == pytest.approx(40.0)
    assert values["lmtd_k"] == pytest.approx(81.95549, rel=1e-6)
    assert values["pressure_margin_pa"] == pytest.approx(0.0)


def test_case_004_explains_ua_sensitivity_and_nominal_pressure_order() -> None:
    case = _case("004")
    values = case_004_analysis(case)
    sensitivity = case_004_sensitivity_frame(case)

    assert values["q_hot_kw"] == pytest.approx(1064.856763, rel=1e-8)
    assert values["q_cold_kw"] == pytest.approx(1064.856752, rel=1e-8)
    assert values["energy_residual_kw"] == pytest.approx(1.12136e-5, rel=5e-4)
    assert values["lmtd_k"] == pytest.approx(81.91194, rel=1e-7)
    assert values["u_w_m2_k"] == pytest.approx(1000.0)
    assert values["area_m2"] == pytest.approx(13.0)
    assert values["ua_w_k"] == pytest.approx(13000.0)
    assert values["pressure_margin_inlet_pa"] == pytest.approx(50000.0)
    assert values["pressure_margin_outlet_pa"] == pytest.approx(50000.0)
    assert len(sensitivity) >= 12
    assert {
        "U (W/(m²·K))",
        "Caudal frío (kg/s)",
        "Carga térmica (kW)",
    }.issubset(sensitivity.columns)


def test_portfolio_preserves_validation_and_lifecycle_dimensions() -> None:
    portfolio = portfolio_frame(load_all_cases(ROOT)).set_index("ID")
    assert portfolio.loc["001", "Validación"] == "PASS"
    assert portfolio.loc["001", "Ciclo de vida"] == "validated"
    assert portfolio.loc["002", "Validación"] == "FAIL"
    assert portfolio.loc["002", "Ciclo de vida"] == "review"
    assert portfolio.loc["003", "Validación"] == "CONDITIONAL"
    assert portfolio.loc["004", "Validación"] == "CONDITIONAL"
    assert portfolio.loc["004", "Ciclo de vida"] == "review"


def test_case_002_failure_is_data_quality_not_physical_balance() -> None:
    criteria = criteria_frame(_case("002"))
    failures = criteria.loc[criteria["Estado"] == "FAIL"]
    assert len(failures) == 1
    assert failures.iloc[0]["Alcance"] == "data_quality"
    assert not criteria.loc[
        criteria["Alcance"].isin(["numerical", "phenomenon"]), "Estado"
    ].eq("FAIL").any()


def test_process_datasets_have_material_streams_and_core_variables() -> None:
    for case in load_all_cases(ROOT):
        streams = material_streams(case)
        assert not streams.empty
        assert streams["object_id"].is_unique
        assert {
            "temperature_K",
            "pressure_Pa",
            "mass_flow_kg_s",
        }.issubset(streams.columns)


def test_streamlit_default_view_is_a_scientific_learning_map() -> None:
    app = AppTest.from_file(str(MODULE_DIR / "app.py"), default_timeout=75).run()
    assert not app.exception
    assert app.title[0].value == (
        "Fenómenos científicos e ingeniería explicados con evidencia"
    )
    assert any(item.value == "Mapa de aprendizaje" for item in app.subheader)
    assert not any("Criterios PASS" in str(item.value) for item in app.metric)


def test_streamlit_scientific_views_and_limits_render() -> None:
    app = AppTest.from_file(str(MODULE_DIR / "app.py"), default_timeout=75).run()

    app.sidebar.radio[0].set_value("Estudiar un caso").run(timeout=75)
    assert not app.exception
    assert len(app.selectbox[0].options) == 4

    case_002 = next(option for option in app.selectbox[0].options if option.startswith("002"))
    app.selectbox[0].set_value(case_002).run(timeout=75)
    assert not app.exception
    assert any("no constituye validación experimental" in item.value for item in app.warning)

    case_003 = next(option for option in app.selectbox[0].options if option.startswith("003"))
    app.selectbox[0].set_value(case_003).run(timeout=75)
    assert not app.exception
    assert any("0 Pa" in item.value for item in app.warning)

    case_004 = next(option for option in app.selectbox[0].options if option.startswith("004"))
    app.selectbox[0].set_value(case_004).run(timeout=75)
    assert not app.exception
    assert any("+50 kPa" in item.value for item in app.warning)
    assert any("+27.22 %" in item.value for item in app.warning)

    app.sidebar.radio[0].set_value("Conectar fenómenos").run(timeout=75)
    assert not app.exception
    assert any("Conectar fenómenos entre casos" in item.value for item in app.subheader)

    app.sidebar.radio[0].set_value("Rigor y fuentes").run(timeout=75)
    assert not app.exception
    assert any("Rigor, trazabilidad" in item.value for item in app.subheader)


def test_dashboard_never_declares_white_text() -> None:
    source = (MODULE_DIR / "app.py").read_text(encoding="utf-8").lower()
    theme = (ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8")
    assert "color:white" not in source
    assert "color: white" not in source
    assert 'textColor = "#0F172A"' in theme
