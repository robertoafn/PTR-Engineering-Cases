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
- Curaduría reproducible de casos publicados por FOSSEE, preservando el
  artefacto fuente y separándolo de toda reproducción o variante posterior.
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

v0.6.0 organiza el repositorio en dos líneas de trabajo conectadas, pero con
evidencia y ciclos de vida independientes:

1. **Casos PTR (`cases/`)**: el alcance de desarrollo de los casos 001–004 se
   cierra para este release. Cierre de alcance no significa que todos estén
   validados: 001 conserva `validated/PASS`; 002 permanece `review/FAIL` por la
   discrepancia energética API↔dataset; 003 y 004 permanecen
   `review/CONDITIONAL` por las limitaciones que documentan sus informes.
2. **Casos de literatura (`Literature_cases/`)**: comienza una línea de
   curaduría y reproducción de casos FOSSEE con el Caso 102, *Methanol Water
   Distillation*. Su incorporación inicial verifica identidad, integridad,
   procedencia y licencia del material fuente; no equivale a reconvergencia ni
   a validación científica con DWSIM actual.

El corpus documental de exploración se mantiene únicamente en
`references/Literature_cases_references/`, ruta excluida por `.gitignore`. El
repositorio no publica ese corpus en bloque: sólo promueve a
`Literature_cases/` los casos seleccionados que recorren el flujo de trabajo.
En cada promoción, los originales FOSSEE se conservan sin modificación y se
acompañan con hashes SHA-256, manifiesto, licencia y procedencia.

La siguiente etapa del Caso 102 depende de archivos que aportará el usuario:
una reproducción en DWSIM 9.0.5 y, posteriormente, variantes termodinámicas
separadas —por ejemplo NRTL— cuando correspondan. Esas variantes nunca
sustituirán el archivo FOSSEE original ni heredarán un estado de validación sin
evidencia propia.

El dashboard científico de v0.6.0 explica todavía los casos PTR 001–004. El
Caso 102 se integrará a la interfaz sólo después de disponer de resultados
propios, metadatos y figuras reproducibles; por ahora su evidencia se consulta
directamente en `Literature_cases/`.

El Caso 004 adopta `U = 1000 W/(m²·K)`, `A = 13 m²` y una presión del lado
limpio 50 kPa mayor que la del contaminado. El cierre térmico demuestra
coherencia interna del estado nominal, mientras el margen sólo demuestra el
signo estático impuesto. El cambio de fase advertido por DWSIM, las propiedades
calorimétricas, la validación externa y la seguridad conservan estados y
limitaciones separados. La paridad del Caso 002 fue reejecutada: el estado
termodinámico reproduce el dataset, pero la energía de `MSTR-204` falla el
umbral de 0.05 %, por lo que no se promueven los casos dependientes.

La propagación de incertidumbre GUM/Monte Carlo sobre HX-301 permanece como
trabajo futuro. No se publicarán distribuciones, intervalos o probabilidades
sin presupuesto trazable, correlaciones, implementación reproducible y una
regla de decisión externa cuando se pretenda evaluar conformidad hidráulica.

El Caso 003 extiende la secuencia del Caso 002: reutiliza el condensado líquido
caliente con trazas de metanol como fuente térmica para precalentar agua limpia
en el intercambiador HX-301. Además de los balances de materia y energía,
evalúa la relación `P_limpio - P_contaminado`. El escenario base obtiene
`0 Pa`, condición límite que no aporta margen ni demuestra seguridad
operacional. El caso documenta que una aplicación real debe mantener un
diferencial positivo definido por análisis de riesgos, vigilarlo de forma
continua y complementar la presión con detección de fugas, aislamiento o una
barrera mecánica apropiada.

## Transición PTR Core

La evolución hacia PTR Industrial Decision Core se realizará por capas, sin
reescribir ni reclasificar retrospectivamente la evidencia existente. El
primer bloque introduce la
[política de versiones DWSIM](adr/0001-dwsim-version-policy.md) y el
[contrato `SimulationRun`](11_simulation_run_contract.md).

Este bloque separa el estado guardado de una ejecución real, fija el rol de
cada versión del simulador y crea la frontera gobernada entre los archivos
DWSIM y los futuros datos canónicos. Todavía no promueve las cuatro
simulaciones exploratorias locales ni habilita conclusiones nuevas para el
Caso 102.

## Relación con el proceso productivo

El portafolio no representa una planta Kraft integrada. El Caso 001 modela un
servicio auxiliar de agua previo al lavado de pulpa y es independiente de los
otros casos. Los casos 002, 003 y 004 forman una secuencia conceptual:
expansión y separación flash de un condensado caliente, recuperación indirecta
de calor y revisión del escenario HX-301 con UA y orden nominal de presiones
corregidos. Todas las condiciones son sintéticas o simuladas y no se atribuyen
a una instalación industrial específica.
