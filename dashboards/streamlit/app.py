"""Laboratorio virtual y dashboard científico del portafolio PTR."""

from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go

import streamlit as st

MODULE_DIR = Path(__file__).resolve().parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

from data_model import (  # noqa: E402
    CaseBundle,
    criteria_frame,
    freshness_utc,
    load_all_cases,
    load_catalog,
    repository_root,
)
from science_model import (  # noqa: E402
    case_001_analysis,
    case_001_state_frame,
    case_002_analysis,
    case_002_chromatogram_frame,
    case_002_gc_analysis,
    case_002_split_frame,
    case_003_analysis,
    case_003_temperature_frame,
)

BLUE = "#2563EB"
BLUE_LIGHT = "#DBEAFE"
GOLD = "#D4A017"
GOLD_LIGHT = "#FEF3C7"
ORANGE = "#EA7C2B"
ORANGE_LIGHT = "#FFEDD5"
PINK = "#C23B73"
PINK_LIGHT = "#FCE7F3"
OLIVE = "#77834A"
NEUTRAL = "#64748B"
INK = "#0F172A"
STATUS_COLORS = {
    "PASS": BLUE,
    "CONDITIONAL": ORANGE,
    "FAIL": PINK,
    "NOT_DEMONSTRATED": GOLD,
    "NOT_RUN": NEUTRAL,
    "N_A": NEUTRAL,
}
STATUS_BACKGROUNDS = {
    "PASS": BLUE_LIGHT,
    "CONDITIONAL": ORANGE_LIGHT,
    "FAIL": PINK_LIGHT,
    "NOT_DEMONSTRATED": GOLD_LIGHT,
    "NOT_RUN": "#E2E8F0",
    "N_A": "#E2E8F0",
}
SCOPE_LABELS = {
    "data_quality": "Calidad y reproducibilidad",
    "numerical": "Balances numéricos",
    "phenomenon": "Fenómeno físico/químico",
    "safety": "Integridad y seguridad",
}


st.set_page_config(
    page_title="PTR · Laboratorio virtual",
    page_icon="⚗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.25rem; padding-bottom: 2rem; max-width: 1450px;
    }
    .ptr-kicker {
        color:#1D4ED8; font-weight:750; letter-spacing:.08em;
        text-transform:uppercase;
    }
    .ptr-question {
        background:#EFF6FF; border-left:5px solid #2563EB;
        border-radius:8px; color:#0F172A; font-size:1.08rem;
        line-height:1.55; padding:.9rem 1.05rem;
    }
    .ptr-equation-note {
        background:#F8FAFC; border:1px solid #CBD5E1;
        border-radius:10px; color:#0F172A; line-height:1.55;
        padding:.75rem .9rem;
    }
    .ptr-status {
        display:inline-block; padding:.22rem .62rem; border-radius:999px;
        color:#0F172A; font-weight:700; font-size:.82rem;
    }
    [data-testid="stMetric"] {
        background:#F8FAFC; border:1px solid #E2E8F0;
        padding:.75rem; border-radius:12px;
    }
    [data-testid="stCaptionContainer"] {color:#475569;}
    p, li {line-height:1.55;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def cached_cases() -> list[CaseBundle]:
    return load_all_cases()


@st.cache_data(show_spinner=False)
def cached_catalog() -> dict[str, Any]:
    return load_catalog()


def status_badge(status: str) -> str:
    border = STATUS_COLORS.get(status, NEUTRAL)
    background = STATUS_BACKGROUNDS.get(status, "#E2E8F0")
    return (
        f'<span class="ptr-status" style="background:{background}; '
        f'border:1px solid {border}; color:{INK}">{status}</span>'
    )


def plot_layout(fig: go.Figure, *, height: int = 390) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=24, r=24, t=62, b=42),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(color=INK, family="Arial, sans-serif", size=13),
        title_font=dict(color=INK, size=17),
        legend_title_text="",
        hoverlabel=dict(bgcolor="#FFFFFF", font_color=INK),
    )
    fig.update_traces(textfont_color=INK)
    fig.update_xaxes(showgrid=False, linecolor="#94A3B8", title_font_color=INK)
    fig.update_yaxes(
        gridcolor="#E2E8F0",
        zerolinecolor="#94A3B8",
        linecolor="#94A3B8",
        title_font_color=INK,
    )
    return fig


def vertical_bar(
    frame: pd.DataFrame,
    *,
    x: str,
    y: str,
    title: str,
    unit: str,
    color: str,
    texttemplate: str = "%{y:.4g}",
) -> go.Figure:
    fig = go.Figure(
        go.Bar(
            x=frame[x],
            y=frame[y],
            marker=dict(color=color, line=dict(color=INK, width=0.8)),
            texttemplate=texttemplate,
            textposition="outside",
            cliponaxis=False,
            hovertemplate=f"%{{x}}<br>%{{y:.6g}} {unit}<extra></extra>",
        )
    )
    fig.update_layout(title=title, showlegend=False)
    fig.update_xaxes(title="")
    fig.update_yaxes(title=unit, rangemode="tozero")
    return plot_layout(fig)


def render_header(cases: list[CaseBundle]) -> None:
    st.markdown(
        '<div class="ptr-kicker">PTR Engineering Cases · laboratorio virtual</div>',
        unsafe_allow_html=True,
    )
    st.title("Fenómenos científicos e ingeniería explicados con evidencia")
    st.caption(
        "Cada caso sigue una ruta común: pregunta → flowsheet → mecanismo → "
        "ecuación → datos → interpretación → límites. DWSIM, Python y los métodos "
        "analíticos aportan evidencias complementarias."
    )
    st.caption(
        "Evidencia local versionada · actualización más reciente de resultados: "
        f"{freshness_utc(cases)}"
    )


def render_question(text: str) -> None:
    st.markdown(
        f'<div class="ptr-question"><b>Pregunta científica</b><br>{text}</div>',
        unsafe_allow_html=True,
    )


def render_methods(case: CaseBundle) -> None:
    st.markdown("#### Métodos que aportan evidencia")
    columns = st.columns(len(case.catalog.get("methods", [])) or 1)
    for column, method in zip(
        columns, case.catalog.get("methods", []), strict=False
    ):
        with column:
            with st.container(border=True):
                st.markdown(f"**{method.get('name', 'Método')}**")
                st.write(method.get("role", "Rol no documentado."))


def render_scientific_map(cases: list[CaseBundle], catalog: dict[str, Any]) -> None:
    st.subheader("Mapa de aprendizaje")
    st.write(
        "El portafolio no es un tablero de aprobaciones. Es una secuencia de "
        "experimentos virtuales que usa datos y software para hacer visibles "
        "principios de mecánica de fluidos, termodinámica, equilibrio, química "
        "analítica, transferencia de calor e integridad de proceso."
    )

    for case in cases:
        st.markdown(f"### Caso {case.case_id} · {case.short_title}")
        figure_col, science_col = st.columns([1.2, 1], gap="large")
        with figure_col:
            if case.figure_paths:
                st.image(
                    str(case.figure_paths[0]),
                    caption=case.catalog.get("figure_caption", case.title),
                    width="stretch",
                )
        with science_col:
            render_question(case.catalog.get("scientific_question", "N/D"))
            st.markdown("**Fenómenos que se estudian**")
            for phenomenon in case.catalog.get("phenomena", []):
                st.markdown(
                    f"- **{phenomenon.get('name', 'Fenómeno')}** — "
                    f"{phenomenon.get('category', 'Sin dominio')}"
                )
            st.markdown("**Conclusión científica acotada**")
            st.write(case.catalog.get("conclusion", "Conclusión no declarada."))

        if case.case_id == "001":
            st.info(
                "El Caso 001 es un fundamento independiente de servicios auxiliares; "
                "no alimenta materialmente a los casos 002 o 003."
            )
        if case.case_id == "002":
            st.markdown("#### Puente material 002 → 003")
            cols = st.columns(4)
            cols[0].metric("Corriente", "MSTR-204 → MSTR-301")
            cols[1].metric("Caudal", "≈ 8.95112 kg/s")
            cols[2].metric("Estado", "≈ 406.65 K · 300 kPa")
            cols[3].metric("Metanol", "w ≈ 0.000639")
            st.caption(
                "El Caso 003 reutiliza este estado como base redondeada; las "
                "propiedades restantes se resuelven nuevamente en DWSIM."
            )
        st.divider()

    proposal = catalog.get("proposals", {}).get("004", {})
    st.markdown("### Pregunta siguiente · Caso 004 propuesto")
    render_question(proposal.get("scientific_question", "N/D"))
    st.write(proposal.get("summary", "Propuesta no disponible."))


def render_case_figure(case: CaseBundle) -> None:
    st.markdown("## El flowsheet como mapa del fenómeno")
    figure_col, guide_col = st.columns([1.45, 1], gap="large")
    with figure_col:
        if case.figure_paths:
            st.image(
                str(case.figure_paths[0]),
                caption=case.catalog.get("figure_caption", case.title),
                width="stretch",
            )
        else:
            st.info("El caso no declara una figura de flowsheet.")
    with guide_col:
        st.markdown("### Cómo leer la figura")
        for step in case.catalog.get("figure_guide", []):
            st.markdown(f"**{step.get('label', 'Paso')}**")
            st.write(step.get("text", "Descripción no disponible."))


def render_case_snapshot(case: CaseBundle) -> None:
    st.markdown("### Cambio físico observado")
    if case.case_id == "001":
        values = case_001_analysis(case)
        columns = st.columns(4)
        columns[0].metric("Salto de presión", f"{values['pressure_rise_kpa']:.0f} kPa")
        columns[1].metric("Potencia de bomba", f"{values['pump_power_kw']:.3f} kW")
        columns[2].metric("Aumento térmico", f"{values['temperature_rise_k']:.3f} K")
        ratio = values["heater_duty_kw"] / values["pump_power_kw"]
        columns[3].metric("Carga térmica / bomba", f"{ratio:.2f}×")
    elif case.case_id == "002":
        values = case_002_analysis(case)
        columns = st.columns(4)
        columns[0].metric("Caída de presión", f"{values['pressure_drop_kpa']:.0f} kPa")
        columns[1].metric("Fracción másica de vapor", f"{100*values['vapor_mass_yield']:.3f} %")
        columns[2].metric(
            "Metanol recuperado en vapor",
            f"{100*values['methanol_recovery_vapor']:.3f} %",
        )
        columns[3].metric(
            "Enriquecimiento vapor/líquido",
            f"{values['methanol_enrichment_vapor_liquid']:.3f}×",
        )
        st.caption(
            "El factor vapor/líquido usa fracciones másicas expresadas sobre la "
            "misma base; no compara directamente concentraciones de vial con la fase vapor."
        )
    elif case.case_id == "003":
        values = case_003_analysis(case)
        columns = st.columns(4)
        columns[0].metric("Calor recuperado", f"{values['q_mean_kw']/1000:.5f} MW")
        columns[1].metric("Agua limpia", f"+{values['cold_temperature_rise_k']:.3f} K")
        columns[2].metric("LMTD derivada", f"{values['lmtd_k']:.4f} K")
        columns[3].metric("Margen hidráulico", f"{values['pressure_margin_pa']:.0f} Pa")


def render_case_001_evidence(case: CaseBundle, phenomenon_id: str) -> None:
    values = case_001_analysis(case)
    states = case_001_state_frame(case)
    if phenomenon_id == "elevacion_presion_bomba":
        chart_col, reading_col = st.columns([1.35, 1], gap="large")
        with chart_col:
            fig = vertical_bar(
                states,
                x="Etapa",
                y="Presión (kPa)",
                title="Presión del agua a través de la línea",
                unit="kPa",
                color=BLUE,
                texttemplate="%{y:.1f}",
            )
            st.plotly_chart(fig, width="stretch")
        with reading_col:
            st.markdown("#### Lectura cuantitativa")
            st.metric("Potencia hidráulica útil", f"{values['hydraulic_power_kw']:.3f} kW")
            st.metric("Potencia reportada por P-001", f"{values['pump_power_kw']:.3f} kW")
            st.metric("Eficiencia implícita", f"{100*values['pump_efficiency']:.2f} %")
            st.write(
                "El caudal permanece en 10 kg/s: el salto visible es hidráulico, "
                "no consecuencia de acumulación de masa."
            )
    elif phenomenon_id == "calentamiento_sensible":
        chart_col, reading_col = st.columns([1.35, 1], gap="large")
        with chart_col:
            fig = vertical_bar(
                states,
                x="Etapa",
                y="Temperatura (K)",
                title="Temperatura del agua a través de la línea",
                unit="K",
                color=ORANGE,
                texttemplate="%{y:.3f}",
            )
            st.plotly_chart(fig, width="stretch")
        with reading_col:
            st.markdown("#### Lectura cuantitativa")
            st.metric("Carga de H-001", f"{values['heater_duty_kw']/1000:.6f} MW")
            st.metric("Cambio de temperatura", f"{values['temperature_rise_k']:.3f} K")
            st.metric(
                "cₚ aparente de réplica",
                f"{values['apparent_cp_kj_kg_k']:.4f} kJ/(kg·K)",
            )
            st.write(
                "La carga térmica es mucho mayor que la potencia de bombeo; por "
                "eso la transformación energética está dominada por H-001."
            )
    else:
        fig = vertical_bar(
            states,
            x="Etapa",
            y="Caudal másico (kg/s)",
            title="Caudal másico en las corrientes materiales",
            unit="kg/s",
            color=OLIVE,
            texttemplate="%{y:.3f}",
        )
        st.plotly_chart(fig, width="stretch")
        st.metric("Residuo entrada–salida", f"{values['mass_residual_kg_s']:.3g} kg/s")


def render_case_002_expansion(case: CaseBundle) -> None:
    values = case_002_analysis(case)
    before_after = pd.DataFrame(
        {
            "Estado": ["Antes de válvula", "Después de válvula"],
            "Presión (kPa)": [1200.0, 300.0],
            "Temperatura (K)": [453.15, 406.652761777802],
        }
    )
    pressure_col, temperature_col = st.columns(2, gap="large")
    with pressure_col:
        st.plotly_chart(
            vertical_bar(
                before_after,
                x="Estado",
                y="Presión (kPa)",
                title="Presión antes y después de la válvula",
                unit="kPa",
                color=BLUE,
                texttemplate="%{y:.1f}",
            ),
            width="stretch",
        )
    with temperature_col:
        st.plotly_chart(
            vertical_bar(
                before_after,
                x="Estado",
                y="Temperatura (K)",
                title="Temperatura antes y después de la válvula",
                unit="K",
                color=ORANGE,
                texttemplate="%{y:.3f}",
            ),
            width="stretch",
        )
    cols = st.columns(3)
    cols[0].metric("Δp", f"−{values['pressure_drop_kpa']:.0f} kPa")
    cols[1].metric("ΔT", f"−{values['temperature_drop_k']:.3f} K")
    cols[2].metric("Δh específico", f"{values['enthalpy_change_kj_kg']:.3g} kJ/kg")
    st.caption(
        "Valores derivados del CSV publicado. La entalpía prácticamente constante, "
        "no una conversión directa de presión en temperatura, caracteriza el estrangulamiento."
    )


def render_case_002_partition(case: CaseBundle) -> None:
    values = case_002_analysis(case)
    split = case_002_split_frame(case)
    fig = go.Figure()
    phase_colors = {"Vapor flash": ORANGE, "Líquido residual": BLUE}
    for phase in ["Vapor flash", "Líquido residual"]:
        row = split.loc[split["Fase"].eq(phase)].iloc[0]
        fig.add_trace(
            go.Bar(
                name=phase,
                y=["Masa total", "Metanol"],
                x=[
                    row["Fracción de la alimentación (%)"],
                    row["Recuperación de metanol (%)"],
                ],
                orientation="h",
                marker=dict(
                    color=phase_colors[phase], line=dict(color=INK, width=0.8)
                ),
                texttemplate="%{x:.2f} %",
                textposition="inside",
                insidetextfont=dict(color=INK),
                hovertemplate="%{y}<br>%{x:.5f} %<extra>%{fullData.name}</extra>",
            )
        )
    fig.update_layout(
        title="Reparto de masa total frente al reparto de metanol",
        barmode="stack",
        legend=dict(orientation="h", y=1.13),
    )
    fig.update_xaxes(title="Fracción de la alimentación [%]", range=[0, 100])
    fig.update_yaxes(title="")
    st.plotly_chart(plot_layout(fig, height=360), width="stretch")
    cols = st.columns(3)
    cols[0].metric("Vapor generado", f"{100*values['vapor_mass_yield']:.4f} % de la masa")
    cols[1].metric(
        "Metanol hacia vapor",
        f"{100*values['methanol_recovery_vapor']:.4f} %",
    )
    cols[2].metric(
        "w₍vapor₎ / w₍líquido₎",
        f"{values['methanol_enrichment_vapor_liquid']:.4f}×",
    )
    st.info(
        "El vapor representa una fracción pequeña de la masa, pero captura una "
        "fracción mucho mayor del metanol. Esa diferencia es la evidencia visual "
        "de partición preferente hacia la fase vapor."
    )


def render_case_002_gc(case: CaseBundle) -> None:
    metrics, standards, samples = case_002_gc_analysis(case)
    raw = case_002_chromatogram_frame(case)
    st.markdown("#### 1 · Señal cromatográfica alrededor del pico")
    window = raw.loc[raw["time_s"].between(124.0, 133.0)].copy()
    fig = go.Figure()
    colors = {
        "Blanco": NEUTRAL,
        "Alimentación": BLUE,
        "Vapor condensado": ORANGE,
        "Vapor duplicado": GOLD,
        "Líquido residual": OLIVE,
    }
    for sample in colors:
        subset = window.loc[window["Muestra"].eq(sample)]
        if subset.empty:
            continue
        fig.add_trace(
            go.Scatter(
                x=subset["time_s"],
                y=subset["signal"],
                mode="lines",
                name=sample,
                line=dict(color=colors[sample], width=2),
                hovertemplate="t=%{x:.2f} s<br>señal=%{y:.3f}<extra>%{fullData.name}</extra>",
            )
        )
    fig.update_layout(
        title="Ventana del pico de metanol en señales sintéticas",
        legend=dict(orientation="h", y=1.18),
    )
    fig.update_xaxes(title="Tiempo de retención [s]")
    fig.update_yaxes(title="Señal relativa [u.a.]")
    st.plotly_chart(plot_layout(fig, height=420), width="stretch")
    st.caption(
        "Se muestran puntos crudos de archivos OpenChrom entre 124 y 133 s. "
        "La respuesta es relativa; no representa una señal instrumental calibrada real."
    )

    st.markdown("#### 2 · De la señal a la concentración")
    calibration_col, sample_col = st.columns(2, gap="large")
    with calibration_col:
        x_values = standards["Concentración (kg/m³)"].to_numpy()
        x_fit = np.linspace(float(x_values.min()), float(x_values.max()), 100)
        y_fit = metrics["slope"] * x_fit + metrics["intercept"]
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=standards["Área integrada"],
                mode="markers",
                name="Estándares",
                marker=dict(color=BLUE, size=10, line=dict(color=INK, width=1)),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=x_fit,
                y=y_fit,
                mode="lines",
                name="Ajuste lineal",
                line=dict(color=INK, width=2, dash="dash"),
            )
        )
        fig.update_layout(title="Calibración lineal sintética")
        fig.update_xaxes(title="Concentración de vial [kg/m³]")
        fig.update_yaxes(title="Respuesta relativa integrada [u.a.]")
        st.plotly_chart(plot_layout(fig), width="stretch")
        st.latex(
            rf"A={metrics['slope']:.5f}\,C{metrics['intercept']:+.5f},\quad "
            rf"R^2={metrics['r_squared']:.8f}"
        )
    with sample_col:
        fig = go.Figure(
            go.Bar(
                x=samples["sample_id"],
                y=samples["Concentración en corriente (kg/m³)"],
                marker=dict(color=PINK, line=dict(color=INK, width=0.8)),
                texttemplate="%{y:.4f}",
                textposition="outside",
                cliponaxis=False,
            )
        )
        fig.update_layout(title="Concentraciones reconstruidas de las muestras")
        fig.update_xaxes(title="Muestra")
        fig.update_yaxes(title="Concentración en corriente [kg/m³]")
        st.plotly_chart(plot_layout(fig), width="stretch")
        st.metric(
            "RPD de áreas del duplicado MSTR-203",
            f"{metrics['duplicate_rpd_percent']:.4f} %",
        )
    st.warning(
        "OpenChrom importó y visualizó la señal, pero las áreas canónicas se "
        "reconstruyeron externamente por trapecios. La coherencia con DWSIM es "
        "sintética y no constituye validación experimental independiente."
    )


def render_case_002_evidence(case: CaseBundle, phenomenon_id: str) -> None:
    if phenomenon_id == "expansion_isoentalpica":
        render_case_002_expansion(case)
    elif phenomenon_id == "equilibrio_y_particion":
        render_case_002_partition(case)
    else:
        render_case_002_gc(case)


def case_003_temperature_figure(case: CaseBundle) -> go.Figure:
    values = case_003_analysis(case)
    frame = case_003_temperature_frame(case)
    temperatures = dict(zip(frame["Corriente"], frame["Temperatura (K)"], strict=True))
    extremes = ["Extremo A", "Extremo B"]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=extremes,
            y=[temperatures["MSTR-301"], temperatures["MSTR-303"]],
            mode="lines+markers+text",
            name="Condensado: MSTR-301 → MSTR-303",
            line=dict(color=ORANGE, width=3),
            marker=dict(size=11, color=ORANGE, line=dict(color=INK, width=1)),
            text=[f"{temperatures['MSTR-301']:.3f} K", f"{temperatures['MSTR-303']:.3f} K"],
            textposition="top center",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=extremes,
            y=[temperatures["MSTR-304"], temperatures["MSTR-302"]],
            mode="lines+markers+text",
            name="Agua limpia: MSTR-302 ← MSTR-304",
            line=dict(color=BLUE, width=3, dash="dash"),
            marker=dict(size=11, color=BLUE_LIGHT, line=dict(color=BLUE, width=2)),
            text=[f"{temperatures['MSTR-304']:.3f} K", f"{temperatures['MSTR-302']:.3f} K"],
            textposition="bottom center",
        )
    )
    fig.add_annotation(
        x="Extremo A",
        y=(temperatures["MSTR-301"] + temperatures["MSTR-304"]) / 2,
        text=f"ΔT₁={values['delta_t_terminal_1_k']:.3f} K",
        showarrow=False,
        font=dict(color=INK),
    )
    fig.add_annotation(
        x="Extremo B",
        y=(temperatures["MSTR-303"] + temperatures["MSTR-302"]) / 2,
        text=f"ΔT₂={values['delta_t_terminal_2_k']:.3f} K",
        showarrow=False,
        font=dict(color=INK),
    )
    fig.update_layout(
        title="Temperaturas terminales en disposición contracorriente",
        legend=dict(orientation="h", y=1.18),
    )
    fig.update_xaxes(title="Extremos físicos de HX-301")
    fig.update_yaxes(title="Temperatura [K]")
    return plot_layout(fig, height=430)


def render_case_003_heat(case: CaseBundle) -> None:
    values = case_003_analysis(case)
    st.plotly_chart(
        case_003_temperature_figure(case),
        width="stretch",
        key="case003_temperature_heat",
    )
    heat = pd.DataFrame(
        {
            "Balance": ["Cedida por condensado", "Recibida por agua"],
            "Carga (kW)": [values["q_hot_kw"], values["q_cold_kw"]],
        }
    )
    chart_col, reading_col = st.columns([1.25, 1], gap="large")
    with chart_col:
        st.plotly_chart(
            vertical_bar(
                heat,
                x="Balance",
                y="Carga (kW)",
                title="Carga calculada desde cada lado",
                unit="kW",
                color=ORANGE,
                texttemplate="%{y:.3f}",
            ),
            width="stretch",
        )
    with reading_col:
        st.markdown("#### Lectura cuantitativa")
        st.metric("Q̇ promedio derivado del CSV", f"{values['q_mean_kw']:.3f} kW")
        st.metric("Residuo Q̇ₕ − Q̇꜀", f"{values['energy_residual_kw']:.6f} kW")
        st.write(
            "Las dos rutas de cálculo convergen en la misma escala de carga. "
            "Esto respalda el intercambio térmico dentro de la precisión del CSV."
        )
        st.caption(
            "La sección de rigor mantiene separada esta derivación redondeada del "
            "resultado obtenido por DWSIM Automation API con mayor precisión."
        )


def render_case_003_lmtd(case: CaseBundle) -> None:
    values = case_003_analysis(case)
    st.plotly_chart(
        case_003_temperature_figure(case),
        width="stretch",
        key="case003_temperature_lmtd",
    )
    columns = st.columns(4)
    columns[0].metric("ΔT₁", f"{values['delta_t_terminal_1_k']:.3f} K")
    columns[1].metric("ΔT₂", f"{values['delta_t_terminal_2_k']:.3f} K")
    columns[2].metric("LMTD", f"{values['lmtd_k']:.5f} K")
    columns[3].metric("U aparente", f"{values['u_inferred_w_m2_k']:.1f} W/(m²·K)")
    st.info(
        "U se infiere dentro del escenario con A=1 m² y F=1. No es una medición "
        "de desempeño ni el dimensionamiento de un intercambiador industrial."
    )


def render_case_003_pressure(case: CaseBundle) -> None:
    values = case_003_analysis(case)
    pressure = pd.DataFrame(
        {
            "Lado": ["Agua limpia", "Condensado con trazas"],
            "Presión (kPa)": [
                values["pressure_clean_pa"] / 1000.0,
                values["pressure_contaminated_pa"] / 1000.0,
            ],
        }
    )
    fig = vertical_bar(
        pressure,
        x="Lado",
        y="Presión (kPa)",
        title="Presión de salida en ambos lados de HX-301",
        unit="kPa",
        color=GOLD,
        texttemplate="%{y:.1f}",
    )
    st.plotly_chart(fig, width="stretch")
    st.metric("pₗᵢₘₚᵢₒ − p꜀ₒₙₜₐₘᵢₙₐdₒ", f"{values['pressure_margin_pa']:.0f} Pa")
    st.warning(
        "Las barras coinciden: 0 Pa es una frontera sin dirección hidráulica "
        "preferente. No es margen positivo ni evidencia de control de contaminación."
    )
    st.caption(
        "El agua limpia permanece sin metanol porque el modelo no incluye fuga ni "
        "transferencia de masa; esa condición de modelación no demuestra integridad."
    )


def render_case_003_evidence(case: CaseBundle, phenomenon_id: str) -> None:
    if phenomenon_id == "transferencia_calor_indirecta":
        render_case_003_heat(case)
    elif phenomenon_id == "fuerza_impulsora_lmtd":
        render_case_003_lmtd(case)
    else:
        render_case_003_pressure(case)


def render_criterion_evidence(case: CaseBundle, criterion_ids: list[str]) -> None:
    rows = []
    for criterion in case.validation.get("criteria", []):
        if criterion.get("id") not in criterion_ids:
            continue
        result = criterion.get("result") or {}
        rows.append(
            {
                "Criterio": criterion.get("title", criterion.get("id")),
                "Alcance": SCOPE_LABELS.get(
                    criterion.get("scope"), criterion.get("scope", "N/D")
                ),
                "Resultado": result.get("value"),
                "Unidad": result.get("unit", ""),
                "Estado": criterion.get("status", "NOT_RUN"),
                "Fuente": criterion.get("evidence_source", "N/D"),
            }
        )
    if rows:
        st.table(pd.DataFrame(rows))
    else:
        st.info("No se encontró evidencia estructurada para este fenómeno.")


def render_phenomenon(case: CaseBundle, phenomenon: dict[str, Any]) -> None:
    st.markdown(f"## {phenomenon.get('name', 'Fenómeno')}")
    st.markdown(f"**Pregunta guía:** {phenomenon.get('question', 'N/D')}")
    mechanism_col, model_col = st.columns([1.15, 1], gap="large")
    with mechanism_col:
        st.markdown("### Qué ocurre físicamente")
        st.write(phenomenon.get("explanation", "Explicación no declarada."))
    with model_col:
        st.markdown("### Modelo mínimo")
        st.latex(phenomenon.get("equation_latex", phenomenon.get("equation", "N/A")))
        st.markdown(
            '<div class="ptr-equation-note"><b>Variables</b></div>',
            unsafe_allow_html=True,
        )
        for variable in phenomenon.get("variables", []):
            st.markdown(f"- {variable}")

    st.markdown("### Qué muestran los datos")
    renderers: dict[str, Callable[[CaseBundle, str], None]] = {
        "001": render_case_001_evidence,
        "002": render_case_002_evidence,
        "003": render_case_003_evidence,
    }
    renderer = renderers.get(case.case_id)
    if renderer is None:
        st.info("Aún no existe una visualización científica específica para este caso.")
    else:
        renderer(case, str(phenomenon.get("id")))

    interpretation_col, limit_col = st.columns(2, gap="large")
    with interpretation_col:
        st.markdown("### Lectura de ingeniería")
        st.write(phenomenon.get("engineering_meaning", "Interpretación no declarada."))
    with limit_col:
        st.markdown("### Lo que estos datos no demuestran")
        st.write(phenomenon.get("limitation", "Limitación no declarada."))

    with st.expander("Rigor cuantitativo detrás de esta explicación"):
        st.write(phenomenon.get("data_reading", "Lectura de datos no declarada."))
        render_criterion_evidence(case, phenomenon.get("evidence_criteria", []))


def render_case_study(cases: list[CaseBundle]) -> None:
    labels = {f"{case.case_id} · {case.short_title}": case for case in cases}
    selected_label = st.selectbox(
        "Seleccione el experimento virtual",
        options=list(labels),
        key="case_selector",
    )
    case = labels[selected_label]

    st.markdown(f"# Caso {case.case_id} · {case.title}")
    render_question(case.catalog.get("scientific_question", "N/D"))
    st.write(case.catalog.get("summary", "Resumen no declarado."))

    st.markdown("### Objetivos de aprendizaje")
    for outcome in case.catalog.get("learning_outcomes", []):
        st.markdown(f"- {outcome}")

    render_case_figure(case)
    render_case_snapshot(case)
    render_methods(case)

    st.markdown("## Explorar los fenómenos")
    phenomena = case.catalog.get("phenomena", [])
    tabs = st.tabs([item.get("name", "Fenómeno") for item in phenomena])
    for tab, phenomenon in zip(tabs, phenomena, strict=True):
        with tab:
            render_phenomenon(case, phenomenon)

    st.markdown("## Conclusión del caso")
    conclusion_col, limits_col = st.columns(2, gap="large")
    with conclusion_col:
        st.success(case.catalog.get("conclusion", "Conclusión no declarada."))
    with limits_col:
        st.warning(case.catalog.get("limitations", "Limitaciones no declaradas."))


def render_connections(cases: list[CaseBundle]) -> None:
    st.subheader("Conectar fenómenos entre casos")
    st.write(
        "Esta vista compara mecanismos, no resultados de aprobación. Seleccione "
        "un dominio para observar cómo cambia la pregunta y qué evidencia utiliza."
    )
    records = [
        (case, phenomenon)
        for case in cases
        for phenomenon in case.catalog.get("phenomena", [])
    ]
    categories = sorted({item[1].get("category", "Sin dominio") for item in records})
    selected = st.selectbox("Dominio científico", categories, key="domain_selector")
    selected_records = [
        item for item in records if item[1].get("category", "Sin dominio") == selected
    ]

    for case, phenomenon in selected_records:
        with st.container(border=True):
            title_col, figure_col = st.columns([1.25, 1], gap="large")
            with title_col:
                st.markdown(
                    f"### Caso {case.case_id} · {phenomenon.get('name', 'Fenómeno')}"
                )
                st.markdown(f"**Pregunta:** {phenomenon.get('question', 'N/D')}")
                st.write(phenomenon.get("explanation", "Explicación no declarada."))
                st.latex(
                    phenomenon.get(
                        "equation_latex", phenomenon.get("equation", "N/A")
                    )
                )
                st.markdown("**Lectura de ingeniería**")
                st.write(phenomenon.get("engineering_meaning", "N/D"))
            with figure_col:
                if case.figure_paths:
                    st.image(
                        str(case.figure_paths[0]),
                        caption=case.catalog.get("figure_caption", case.title),
                        width="stretch",
                    )

    st.markdown("### Conexiones clave del portafolio")
    st.markdown(
        """
        - **Energía:** P-001 aporta trabajo de eje, H-001 aporta calor y HX-301
          transfiere energía entre dos corrientes sin mezclarlas.
        - **Equilibrio y composición:** la válvula cambia el estado accesible a
          entalpía casi constante; el equilibrio reparte masa y metanol de manera distinta.
        - **Medición:** GC-FID y su calibración muestran cómo una señal se convierte
          en evidencia composicional, aunque en este repositorio los datos sean sintéticos.
        - **Integridad:** que un balance térmico cierre no demuestra una barrera
          hidráulica ni la ausencia de fuga.
        """
    )


def render_rigor(cases: list[CaseBundle], catalog: dict[str, Any]) -> None:
    st.subheader("Rigor, trazabilidad y límites de la evidencia")
    st.write(
        "La explicación científica se apoya en artefactos auditables. Esta vista "
        "concentra los controles para que permanezcan disponibles sin convertirlos "
        "en el objetivo principal del portafolio."
    )
    labels = {f"{case.case_id} · {case.short_title}": case for case in cases}
    selected_label = st.selectbox("Caso", list(labels), key="rigor_case_selector")
    case = labels[selected_label]

    status_col, lifecycle_col, version_col, source_col = st.columns(4)
    status_col.markdown("**Resultado automático**")
    status_col.markdown(status_badge(case.overall_status), unsafe_allow_html=True)
    lifecycle_col.metric("Ciclo de vida", case.lifecycle_status)
    version_col.metric("Versión", case.version)
    source_col.metric("Fuente publicada", case.validation.get("actual_source", "N/D"))

    if case.case_id == "002":
        st.warning(
            "El FAIL publicado corresponde a una discrepancia de 0,11555 % entre "
            "DWSIM API y CSV para la energía de MSTR-204. Los balances y fenómenos "
            "de flash/partición permanecen conformes; no confundir ambas dimensiones."
        )
    if case.case_id == "003":
        st.warning(
            "El estado CONDITIONAL conserva el límite científico principal: "
            "la transferencia térmica pasa, pero Δp limpio–contaminado = 0 Pa."
        )

    render_methods(case)
    st.markdown("### Matriz completa de criterios")
    criteria = criteria_frame(case)
    criteria["Alcance"] = criteria["Alcance"].map(SCOPE_LABELS).fillna(
        criteria["Alcance"]
    )
    st.dataframe(
        criteria[
            ["Alcance", "Criterio", "Estado", "Resultado", "Unidad", "Umbral", "Fuente"]
        ],
        hide_index=True,
        width="stretch",
    )

    with st.expander("Datasets fuente y filas publicadas"):
        if not case.datasets:
            st.info("No hay datasets CSV declarados.")
        for key, frame in case.datasets.items():
            source = case.dataset_paths[key]
            st.markdown(f"**{source.relative_to(repository_root()).as_posix()}**")
            st.dataframe(frame, hide_index=True, width="stretch")

    st.markdown("### Contrato de interpretación")
    st.markdown(
        """
        - Un balance o réplica conforme respalda una relación cuantitativa declarada.
        - `PASS` no significa validación experimental ni aptitud para diseño industrial.
        - Un dato sintético demuestra el método reproducible, no el desempeño de una planta.
        - Las cifras derivadas del CSV y las obtenidas por API se identifican por su fuente.
        - Seguridad e integridad requieren análisis adicionales fuera de este dashboard.
        """
    )

    proposal = catalog.get("proposals", {}).get("004", {})
    st.markdown("### Caso 004 propuesto")
    st.write(proposal.get("summary", "Propuesta no disponible."))
    st.code(proposal.get("document", "N/D"), language=None)


def main() -> None:
    try:
        cases = cached_cases()
        catalog = cached_catalog()
    except (FileNotFoundError, ValueError, OSError, KeyError) as exc:
        st.error(f"No fue posible cargar la evidencia del repositorio: {exc}")
        st.stop()
    if not cases:
        st.warning("No se encontraron casos implementados con evidencia estructurada.")
        st.stop()

    render_header(cases)
    section = st.sidebar.radio(
        "Ruta de exploración",
        [
            "Mapa científico",
            "Estudiar un caso",
            "Conectar fenómenos",
            "Rigor y fuentes",
        ],
    )
    st.sidebar.markdown("---")
    st.sidebar.caption(
        "La explicación es el eje principal; validación y trazabilidad permanecen "
        "como evidencia secundaria auditable."
    )

    if section == "Mapa científico":
        render_scientific_map(cases, catalog)
    elif section == "Estudiar un caso":
        render_case_study(cases)
    elif section == "Conectar fenómenos":
        render_connections(cases)
    else:
        render_rigor(cases, catalog)


if __name__ == "__main__":
    main()
