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
v0.3.0 — Release publicado del portafolio con la arquitectura fundacional
(v0.1.0) completa y tres casos integrados: 001 `validated`, 002 `review` y 003
`review`.

El Caso 003 extiende la secuencia del Caso 002: reutiliza el condensado líquido
caliente con trazas de metanol como fuente térmica para precalentar agua limpia
en el intercambiador HX-301. Además de los balances de materia y energía,
evalúa la relación `P_limpio - P_contaminado`. El escenario base obtiene
`0 Pa`, condición límite que no aporta margen ni demuestra seguridad
operacional. El caso documenta que una aplicación real debe mantener un
diferencial positivo definido por análisis de riesgos, vigilarlo de forma
continua y complementar la presión con detección de fugas, aislamiento o una
barrera mecánica apropiada.

## Relación con el proceso productivo

El portafolio no representa una planta Kraft integrada. El Caso 001 modela un
servicio auxiliar de agua previo al lavado de pulpa y es independiente de los
otros casos. Los casos 002 y 003 sí forman una secuencia conceptual: expansión
y separación flash de un condensado caliente, seguida por recuperación
indirecta de calor desde la fase líquida residual para precalentar agua limpia.
Todas las condiciones son sintéticas o simuladas y no se atribuyen a una
instalación industrial específica.
