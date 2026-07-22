# 00 — Overview

## Propósito
PTR Engineering Cases es un portafolio público de **casos reproducibles** de
ingeniería química industrial, donde cada caso documenta la cadena completa:

> fenómeno → fundamento científico → modelo → simulación/procesamiento →
> resultados → validación/QC → trazabilidad → conclusión técnica

## Alcance
- Simulación de procesos (DWSIM, balances, equilibrios).
- ETL científico y QA/QC de datos sintéticos/hipotéticos.
- Metrología, propagación de incertidumbre.
- Visualización analítica reproducible (Streamlit, Power BI, Plotly).
- Cuando aplique: cromatografía y espectrometría (JCAMP-DX, mzML).

## Exclusiones
- Datos reales sin licencia compatible.
- Reproducción literal de material con copyright.
- Casos no reproducibles o sin trazabilidad metrológica.

## Público objetivo
- Reclutadores técnicos de industria química, energía, alimentos, farma.
- Ingenieros de procesos, datos científicos, QA/QC y metrólogos.
- Comunidad académica y open-source.

## Estado actual
v0.3.0 (en desarrollo) — Arquitectura fundacional (v0.1.0) completa y tres
casos integrados: 001 `validated`, 002 `review` y 003 `review`.

El Caso 003 extiende la secuencia del Caso 002: reutiliza el condensado líquido
caliente con trazas de metanol como fuente térmica para precalentar agua limpia
en el intercambiador HX-301. Además de los balances de materia y energía,
documenta la condición hidráulica `P_frío - P_caliente >= 0 Pa` como criterio
de control de contaminación cruzada ante una eventual falla de integridad.
