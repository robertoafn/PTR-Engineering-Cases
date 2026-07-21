# Changelog — 003_recuperacion_calor_condensado_y_control_contaminacion_cruzada

## [Unreleased]

## [0.1.0] - 2026-07-21

### Added
- Primera simulación DWSIM 9.0.5 del intercambiador de calor de carcasa y tubos HX-301.
- Contexto industrial de recuperación de calor de condensados y control hidráulico de contaminación cruzada.
- Metadatos del caso, supuestos, informe de validación, checklist QC y referencias bibliográficas.
- Dataset de resultados en `data/process_results_v01.csv` con su sidecar `process_results_v01.meta.yaml`.
- Figura del flowsheet exportada desde DWSIM en `assets/figures/fig_003_01_flowsheet.png`.
- Trazabilidad y procedencia en `provenance.json` con checksums SHA-256 de todos los activos técnicos.

### Validation
- Balance global de masa: PASS (0.0% error).
- Balance global de energía: PASS (0.00066% error).
- Réplica analítica de LMTD y ecuación de diseño térmico del intercambiador: PASS (desviación < 0.01%).
- Criterio de presión no negativa para seguridad de contaminación cruzada: PASS ($\Delta P_{safety} = 0$ Pa).

### Notes
- Datos sintéticos y didácticos basados en la corriente residual líquida del Caso 002.
- Status inicial: `review`.
