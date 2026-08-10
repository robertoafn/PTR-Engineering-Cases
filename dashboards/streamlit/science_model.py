"""Cálculos didácticos derivados de los datasets versionados de PTR.

Las funciones de este módulo no sustituyen a los validadores. Transforman la
misma evidencia publicada en magnitudes útiles para explicar los fenómenos de
cada caso y para construir visualizaciones científicas específicas.
"""

from __future__ import annotations

import re
from math import log
from typing import Any

import numpy as np
import pandas as pd
from data_model import CaseBundle, chromatography_dataset, process_dataset


def _row(case: CaseBundle, object_id: str) -> pd.Series:
    frame = process_dataset(case)
    match = frame.loc[frame["object_id"].astype(str).eq(object_id)]
    if match.empty:
        raise KeyError(f"{case.case_id}: no existe {object_id} en el dataset de proceso")
    return match.iloc[0]


def _metadata_value(case: CaseBundle, section: str, name: str) -> float:
    for item in case.metadata.get(section, []):
        if item.get("name") == name:
            return float(item["value"])
    raise KeyError(f"{case.case_id}: no existe {section}.{name} en metadata.yaml")


def _metadata_value_first(
    case: CaseBundle,
    section: str,
    names: tuple[str, ...],
    *,
    default: float | None = None,
) -> float:
    """Obtiene una magnitud aunque el metadato use un alias editorial."""

    for name in names:
        try:
            return _metadata_value(case, section, name)
        except KeyError:
            continue
    if default is not None:
        return default
    joined = ", ".join(names)
    raise KeyError(
        f"{case.case_id}: no existe ninguno de [{joined}] en {section}"
    )


def _number(row: pd.Series, column: str) -> float:
    value = pd.to_numeric(pd.Series([row[column]]), errors="coerce").iloc[0]
    if pd.isna(value):
        raise ValueError(f"Valor no numérico para {column}")
    return float(value)


def case_001_analysis(case: CaseBundle) -> dict[str, float]:
    inlet = _row(case, "MSTR-001_AGUA_FRIA")
    pressurized = _row(case, "MSTR-002_AGUA_PRESURIZADA")
    outlet = _row(case, "MSTR-003_AGUA_ACONDICIONADA")
    pump = _row(case, "P-001_BOMBA_AGUA")
    heater = _row(case, "H-001_CALENTADOR_AGUA")

    mass_flow = _number(inlet, "mass_flow_kg_s")
    volumetric_flow = mass_flow / _number(inlet, "density_kg_m3")
    pressure_rise = _number(pressurized, "pressure_Pa") - _number(
        inlet, "pressure_Pa"
    )
    hydraulic_power_kw = volumetric_flow * pressure_rise / 1000.0
    pump_power_kw = _number(pump, "energy_flow_W") / 1000.0
    heater_duty_kw = _number(heater, "energy_flow_W") / 1000.0
    temperature_rise = _number(outlet, "temperature_K") - _number(
        pressurized, "temperature_K"
    )

    return {
        "mass_flow_kg_s": mass_flow,
        "pressure_rise_kpa": pressure_rise / 1000.0,
        "volumetric_flow_m3_s": volumetric_flow,
        "hydraulic_power_kw": hydraulic_power_kw,
        "pump_power_kw": pump_power_kw,
        "pump_efficiency": hydraulic_power_kw / pump_power_kw,
        "temperature_rise_k": temperature_rise,
        "heater_duty_kw": heater_duty_kw,
        "apparent_cp_kj_kg_k": heater_duty_kw / (mass_flow * temperature_rise),
        "mass_residual_kg_s": mass_flow - _number(outlet, "mass_flow_kg_s"),
    }


def case_001_state_frame(case: CaseBundle) -> pd.DataFrame:
    ids = [
        "MSTR-001_AGUA_FRIA",
        "MSTR-002_AGUA_PRESURIZADA",
        "MSTR-003_AGUA_ACONDICIONADA",
    ]
    labels = ["Agua fría", "Agua presurizada", "Agua acondicionada"]
    rows = [_row(case, object_id) for object_id in ids]
    return pd.DataFrame(
        {
            "Etapa": labels,
            "Corriente": ids,
            "Temperatura (K)": [_number(row, "temperature_K") for row in rows],
            "Presión (kPa)": [_number(row, "pressure_Pa") / 1000.0 for row in rows],
            "Caudal másico (kg/s)": [
                _number(row, "mass_flow_kg_s") for row in rows
            ],
        }
    )


def case_002_analysis(case: CaseBundle) -> dict[str, float]:
    feed = _row(case, "MSTR-201_CONDENSADO_CALIENTE")
    throttled = _row(case, "MSTR-202_MEZCLA_FLASH")
    vapor = _row(case, "MSTR-203_VAPOR_FLASH")
    liquid = _row(case, "MSTR-204_LIQUIDO_FLASH")

    feed_mass = _number(feed, "mass_flow_kg_s")
    feed_methanol = _number(feed, "methanol_mass_flow_kg_s")
    vapor_mass = _number(vapor, "mass_flow_kg_s")
    vapor_methanol = _number(vapor, "methanol_mass_flow_kg_s")

    return {
        "pressure_drop_kpa": (
            _number(feed, "pressure_Pa") - _number(throttled, "pressure_Pa")
        )
        / 1000.0,
        "temperature_drop_k": _number(feed, "temperature_K")
        - _number(throttled, "temperature_K"),
        "enthalpy_change_kj_kg": _number(throttled, "specific_enthalpy_kJ_kg")
        - _number(feed, "specific_enthalpy_kJ_kg"),
        "vapor_mass_yield": vapor_mass / feed_mass,
        "liquid_mass_yield": _number(liquid, "mass_flow_kg_s") / feed_mass,
        "vapor_molar_fraction_after_valve": _number(
            throttled, "vapor_molar_fraction"
        ),
        "methanol_recovery_vapor": vapor_methanol / feed_methanol,
        "methanol_recovery_liquid": _number(
            liquid, "methanol_mass_flow_kg_s"
        )
        / feed_methanol,
        "methanol_enrichment_vapor": _number(vapor, "methanol_mass_fraction")
        / _number(feed, "methanol_mass_fraction"),
        "methanol_enrichment_vapor_liquid": _number(
            vapor, "methanol_mass_fraction"
        )
        / _number(liquid, "methanol_mass_fraction"),
        "mass_residual_kg_s": feed_mass
        - vapor_mass
        - _number(liquid, "mass_flow_kg_s"),
        "methanol_residual_kg_s": feed_methanol
        - vapor_methanol
        - _number(liquid, "methanol_mass_flow_kg_s"),
    }


def case_002_split_frame(case: CaseBundle) -> pd.DataFrame:
    feed = _row(case, "MSTR-201_CONDENSADO_CALIENTE")
    vapor = _row(case, "MSTR-203_VAPOR_FLASH")
    liquid = _row(case, "MSTR-204_LIQUIDO_FLASH")
    feed_mass = _number(feed, "mass_flow_kg_s")
    feed_methanol = _number(feed, "methanol_mass_flow_kg_s")
    return pd.DataFrame(
        {
            "Fase": ["Vapor flash", "Líquido residual"],
            "Caudal másico (kg/s)": [
                _number(vapor, "mass_flow_kg_s"),
                _number(liquid, "mass_flow_kg_s"),
            ],
            "Fracción de la alimentación (%)": [
                100.0 * _number(vapor, "mass_flow_kg_s") / feed_mass,
                100.0 * _number(liquid, "mass_flow_kg_s") / feed_mass,
            ],
            "Metanol (kg/s)": [
                _number(vapor, "methanol_mass_flow_kg_s"),
                _number(liquid, "methanol_mass_flow_kg_s"),
            ],
            "Recuperación de metanol (%)": [
                100.0 * _number(vapor, "methanol_mass_flow_kg_s") / feed_methanol,
                100.0 * _number(liquid, "methanol_mass_flow_kg_s") / feed_methanol,
            ],
        }
    )


def case_002_gc_analysis(case: CaseBundle) -> tuple[dict[str, float], pd.DataFrame, pd.DataFrame]:
    frame = chromatography_dataset(case)
    if frame.empty:
        raise ValueError("El Caso 002 no contiene dataset cromatográfico")
    standards = frame.loc[
        frame["sample_id"].astype(str).str.contains("STD", case=False, na=False)
    ].copy()
    standards["Concentración (kg/m³)"] = pd.to_numeric(
        standards["concentration_vial_kg_m3"], errors="coerce"
    )
    standards["Área integrada"] = pd.to_numeric(
        standards["integrated_area_signal_s"], errors="coerce"
    )
    standards = standards.dropna(subset=["Concentración (kg/m³)", "Área integrada"])
    slope, intercept = np.polyfit(
        standards["Concentración (kg/m³)"], standards["Área integrada"], 1
    )
    fitted = slope * standards["Concentración (kg/m³)"] + intercept
    ss_res = float(((standards["Área integrada"] - fitted) ** 2).sum())
    ss_tot = float(
        (
            standards["Área integrada"] - standards["Área integrada"].mean()
        ).pow(2).sum()
    )

    samples = frame.loc[
        frame["sample_id"].astype(str).str.contains("MSTR", case=False, na=False)
    ].copy()
    samples["Concentración en corriente (kg/m³)"] = pd.to_numeric(
        samples["concentration_stream_kg_m3"], errors="coerce"
    )
    samples = samples.dropna(subset=["Concentración en corriente (kg/m³)"])
    duplicate = samples.loc[
        samples["sample_id"].astype(str).str.contains("MSTR-203", case=False, na=False),
        "integrated_area_signal_s",
    ]
    duplicate = pd.to_numeric(duplicate, errors="coerce").dropna()
    rpd = (
        100.0
        * abs(float(duplicate.iloc[0]) - float(duplicate.iloc[1]))
        / float(duplicate.mean())
    )
    metrics = {
        "slope": float(slope),
        "intercept": float(intercept),
        "r_squared": 1.0 - ss_res / ss_tot,
        "duplicate_rpd_percent": rpd,
    }
    return metrics, standards, samples


def case_002_chromatogram_frame(case: CaseBundle) -> pd.DataFrame:
    """Carga las señales crudas necesarias para explicar el pico de metanol."""

    filenames = {
        "OC-BLK-001.csv": "Blanco",
        "OC-MSTR-201.csv": "Alimentación",
        "OC-MSTR-203.csv": "Vapor condensado",
        "OC-MSTR-203-DUP.csv": "Vapor duplicado",
        "OC-MSTR-204.csv": "Líquido residual",
    }
    raw_dir = case.path / "data" / "raw" / "openchrom"
    frames = []
    for filename, label in filenames.items():
        path = raw_dir / filename
        if not path.is_file():
            continue
        frame = pd.read_csv(path)
        frame["Muestra"] = label
        frame["Archivo"] = filename
        frames.append(frame)
    if not frames:
        return pd.DataFrame(columns=["time_s", "signal", "Muestra", "Archivo"])
    return pd.concat(frames, ignore_index=True)


def case_003_analysis(case: CaseBundle) -> dict[str, float]:
    hot_in = _row(case, "MSTR-301_CONDENSADO_CALIENTE")
    cold_in = _row(case, "MSTR-302_AGUA_FRIA")
    hot_out = _row(case, "MSTR-303_CONDENSADO_ENFRIADO")
    cold_out = _row(case, "MSTR-304_AGUA_PRECALENTADA")

    q_hot_kw = _number(hot_in, "mass_flow_kg_s") * (
        _number(hot_in, "specific_enthalpy_kJ_kg")
        - _number(hot_out, "specific_enthalpy_kJ_kg")
    )
    q_cold_kw = _number(cold_in, "mass_flow_kg_s") * (
        _number(cold_out, "specific_enthalpy_kJ_kg")
        - _number(cold_in, "specific_enthalpy_kJ_kg")
    )
    delta_t_terminal_1 = _number(hot_in, "temperature_K") - _number(
        cold_out, "temperature_K"
    )
    delta_t_terminal_2 = _number(hot_out, "temperature_K") - _number(
        cold_in, "temperature_K"
    )
    lmtd = (delta_t_terminal_2 - delta_t_terminal_1) / log(
        delta_t_terminal_2 / delta_t_terminal_1
    )
    area_m2 = _metadata_value(case, "inputs", "area_intercambio")
    q_mean_kw = (q_hot_kw + q_cold_kw) / 2.0
    pressure_margin_pa = _number(cold_out, "pressure_Pa") - _number(
        hot_out, "pressure_Pa"
    )

    return {
        "q_hot_kw": q_hot_kw,
        "q_cold_kw": q_cold_kw,
        "q_mean_kw": q_mean_kw,
        "energy_residual_kw": q_hot_kw - q_cold_kw,
        "hot_temperature_drop_k": _number(hot_in, "temperature_K")
        - _number(hot_out, "temperature_K"),
        "cold_temperature_rise_k": _number(cold_out, "temperature_K")
        - _number(cold_in, "temperature_K"),
        "delta_t_terminal_1_k": delta_t_terminal_1,
        "delta_t_terminal_2_k": delta_t_terminal_2,
        "lmtd_k": lmtd,
        "u_inferred_w_m2_k": q_mean_kw * 1000.0 / (area_m2 * lmtd),
        "pressure_clean_pa": _number(cold_out, "pressure_Pa"),
        "pressure_contaminated_pa": _number(hot_out, "pressure_Pa"),
        "pressure_margin_pa": pressure_margin_pa,
    }


def case_003_temperature_frame(case: CaseBundle) -> pd.DataFrame:
    hot_in = _row(case, "MSTR-301_CONDENSADO_CALIENTE")
    cold_in = _row(case, "MSTR-302_AGUA_FRIA")
    hot_out = _row(case, "MSTR-303_CONDENSADO_ENFRIADO")
    cold_out = _row(case, "MSTR-304_AGUA_PRECALENTADA")
    return pd.DataFrame(
        {
            "Posición": ["Entrada", "Salida", "Entrada", "Salida"],
            "Lado": ["Condensado", "Condensado", "Agua limpia", "Agua limpia"],
            "Temperatura (K)": [
                _number(hot_in, "temperature_K"),
                _number(hot_out, "temperature_K"),
                _number(cold_in, "temperature_K"),
                _number(cold_out, "temperature_K"),
            ],
            "Corriente": [
                "MSTR-301",
                "MSTR-303",
                "MSTR-302",
                "MSTR-304",
            ],
        }
    )


def case_004_analysis(case: CaseBundle) -> dict[str, float]:
    """Reconstruye el estado nominal corregido de HX-301 desde su CSV."""

    hot_in = _row(case, "MSTR-301_CONDENSADO_CALIENTE")
    cold_in = _row(case, "MSTR-302_AGUA_FRIA")
    hot_out = _row(case, "MSTR-303_CONDENSADO_ENFRIADO")
    cold_out = _row(case, "MSTR-304_AGUA_PRECALENTADA")

    q_hot_kw = _number(hot_in, "mass_flow_kg_s") * (
        _number(hot_in, "specific_enthalpy_kJ_kg")
        - _number(hot_out, "specific_enthalpy_kJ_kg")
    )
    q_cold_kw = _number(cold_in, "mass_flow_kg_s") * (
        _number(cold_out, "specific_enthalpy_kJ_kg")
        - _number(cold_in, "specific_enthalpy_kJ_kg")
    )
    delta_t_terminal_1 = _number(hot_in, "temperature_K") - _number(
        cold_out, "temperature_K"
    )
    delta_t_terminal_2 = _number(hot_out, "temperature_K") - _number(
        cold_in, "temperature_K"
    )
    lmtd = (delta_t_terminal_2 - delta_t_terminal_1) / log(
        delta_t_terminal_2 / delta_t_terminal_1
    )
    area_m2 = _metadata_value_first(
        case,
        "inputs",
        ("area_intercambio", "area_intercambio_m2", "area_hx301"),
        default=13.0,
    )
    u_w_m2_k = _metadata_value_first(
        case,
        "inputs",
        (
            "coeficiente_global_u",
            "coeficiente_global_U",
            "coeficiente_global_transferencia",
            "u_hx301",
        ),
        default=1000.0,
    )
    correction_factor = _metadata_value_first(
        case,
        "inputs",
        ("factor_correccion_lmtd", "factor_correccion_F", "factor_f"),
        default=1.0,
    )
    q_mean_kw = (q_hot_kw + q_cold_kw) / 2.0
    pressure_margin_inlet_pa = _number(cold_in, "pressure_Pa") - _number(
        hot_in, "pressure_Pa"
    )
    pressure_margin_outlet_pa = _number(cold_out, "pressure_Pa") - _number(
        hot_out, "pressure_Pa"
    )
    cold_temperature_rise = _number(cold_out, "temperature_K") - _number(
        cold_in, "temperature_K"
    )

    return {
        "q_hot_kw": q_hot_kw,
        "q_cold_kw": q_cold_kw,
        "q_mean_kw": q_mean_kw,
        "q_ua_kw": u_w_m2_k * area_m2 * correction_factor * lmtd / 1000.0,
        "energy_residual_kw": q_hot_kw - q_cold_kw,
        "hot_temperature_drop_k": _number(hot_in, "temperature_K")
        - _number(hot_out, "temperature_K"),
        "cold_temperature_rise_k": cold_temperature_rise,
        "delta_t_terminal_1_k": delta_t_terminal_1,
        "delta_t_terminal_2_k": delta_t_terminal_2,
        "lmtd_k": lmtd,
        "area_m2": area_m2,
        "u_w_m2_k": u_w_m2_k,
        "ua_w_k": u_w_m2_k * area_m2,
        "correction_factor": correction_factor,
        "effective_cp_cold_kj_kg_k": (
            _number(cold_out, "specific_enthalpy_kJ_kg")
            - _number(cold_in, "specific_enthalpy_kJ_kg")
        )
        / cold_temperature_rise,
        "pressure_clean_inlet_pa": _number(cold_in, "pressure_Pa"),
        "pressure_contaminated_inlet_pa": _number(hot_in, "pressure_Pa"),
        "pressure_clean_outlet_pa": _number(cold_out, "pressure_Pa"),
        "pressure_contaminated_outlet_pa": _number(hot_out, "pressure_Pa"),
        "pressure_margin_inlet_pa": pressure_margin_inlet_pa,
        "pressure_margin_outlet_pa": pressure_margin_outlet_pa,
        "hot_pressure_drop_pa": _number(hot_in, "pressure_Pa")
        - _number(hot_out, "pressure_Pa"),
        "cold_pressure_drop_pa": _number(cold_in, "pressure_Pa")
        - _number(cold_out, "pressure_Pa"),
    }


def case_004_temperature_frame(case: CaseBundle) -> pd.DataFrame:
    hot_in = _row(case, "MSTR-301_CONDENSADO_CALIENTE")
    cold_in = _row(case, "MSTR-302_AGUA_FRIA")
    hot_out = _row(case, "MSTR-303_CONDENSADO_ENFRIADO")
    cold_out = _row(case, "MSTR-304_AGUA_PRECALENTADA")
    return pd.DataFrame(
        {
            "Posición": ["Entrada", "Salida", "Entrada", "Salida"],
            "Lado": ["Condensado", "Condensado", "Agua limpia", "Agua limpia"],
            "Temperatura (K)": [
                _number(hot_in, "temperature_K"),
                _number(hot_out, "temperature_K"),
                _number(cold_in, "temperature_K"),
                _number(cold_out, "temperature_K"),
            ],
            "Corriente": ["MSTR-301", "MSTR-303", "MSTR-302", "MSTR-304"],
        }
    )


def _normalized_column(name: object) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(name).casefold()).strip("_")


def case_004_sensitivity_frame(case: CaseBundle) -> pd.DataFrame:
    """Normaliza el barrido U–caudal sin fijar el esquema del exportador."""

    frame = next(
        (
            dataset.copy()
            for key, dataset in case.datasets.items()
            if key.startswith("hx301_sensitivity") or key.startswith("sensitivity")
        ),
        pd.DataFrame(),
    )
    if frame.empty:
        fallback = case.path / "data" / "processed" / "hx301_sensitivity_v01.csv"
        if fallback.is_file():
            frame = pd.read_csv(fallback)
    if frame.empty:
        return frame

    aliases = {
        "U (W/(m²·K))": {
            "u_w_m2_k",
            "u_w_m_2_k",
            "overall_coefficient_w_m2_k",
            "overall_heat_transfer_coefficient_w_m2_k",
            "u",
        },
        "Caudal frío (kg/s)": {
            "cold_mass_flow_kg_s",
            "cold_flow_kg_s",
            "mass_flow_cold_kg_s",
            "caudal_frio_kg_s",
        },
        "Carga térmica (kW)": {
            "heat_duty_kw",
            "duty_kw",
            "q_kw",
            "q_k_w",
            "heat_load_kw",
        },
        "T salida caliente (K)": {
            "hot_outlet_temperature_k",
            "temperature_hot_out_k",
            "t_hot_out_k",
            "t_out_hot_k",
        },
        "T salida fría (K)": {
            "cold_outlet_temperature_k",
            "temperature_cold_out_k",
            "t_cold_out_k",
            "t_out_cold_k",
        },
        "Margen limpio−contaminado (Pa)": {
            "pressure_margin_pa",
            "delta_p_clean_contaminated_pa",
            "delta_p_clean_minus_contaminated_pa",
            "clean_to_contaminated_deltap_pa",
            "delta_p_pa",
        },
    }
    normalized = {_normalized_column(column): column for column in frame.columns}
    renames: dict[object, str] = {}
    for canonical, options in aliases.items():
        for option in options:
            if option in normalized:
                renames[normalized[option]] = canonical
                break
    return frame.rename(columns=renames)


def scientific_analysis(case: CaseBundle) -> dict[str, Any]:
    """Despacha el cálculo didáctico principal de un caso implementado."""

    dispatch = {
        "001": case_001_analysis,
        "002": case_002_analysis,
        "003": case_003_analysis,
        "004": case_004_analysis,
    }
    try:
        return dispatch[case.case_id](case)
    except KeyError as exc:
        raise NotImplementedError(
            f"No existe transformación científica para el Caso {case.case_id}"
        ) from exc
