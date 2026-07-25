# Changelog — 003_recuperacion_calor_condensado_y_control_contaminacion_cruzada

## [Unreleased]

### Changed
- Separada la validación térmica del tamiz de seguridad operacional.
- Reclasificado $\Delta P_{clean}=0$ Pa como condición límite sin margen; el
  control de contaminación cruzada queda `NOT DEMONSTRATED`.
- Añadidas limitaciones sobre dinámica, pérdidas de carga, fuga, integridad
  mecánica, instrumentación y análisis de riesgos.

### Fixed
- Corregido `energy_flow_kW` de `MSTR-303` para mantener consistencia con el
  caudal másico y la entalpía específica publicados.

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
- Tamiz inicial de presión: $\Delta P_{clean}=0$ Pa, posteriormente
  reclasificado en `[Unreleased]` como condición sin margen.

### Notes
- Datos sintéticos y didácticos basados en la corriente residual líquida del Caso 002.
- Status inicial: `review`.
