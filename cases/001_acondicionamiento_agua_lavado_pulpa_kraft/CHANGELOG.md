# Changelog — 001_acondicionamiento_agua_lavado_pulpa_kraft

## [Unreleased]

## [0.1.1] - 2026-07-17

### Changed
- Estado actualizado de `review` a `validated`.
- Versión del caso actualizada de `0.1.0` a `0.1.1`.
- Informe de validación ampliado con la reapertura, resolución e inspección visual
  realizada por el autor en DWSIM 9.0.5.
- Checklist QC cerrado para los criterios bloqueantes.
- Procedencia actualizada con la actividad `act:author_validation`.

### Validation
- Archivo `.dwxmz` abierto desde la ruta versionada del caso: PASS.
- Resolución estacionaria del flowsheet: PASS.
- Concordancia de topología: PASS.
- Concordancia de potencia de bomba y carga térmica: PASS.
- Veredicto general del Caso 001: `validated`.

### Notes
- La exportación del flowsheet a PNG o JPG queda como mejora visual no bloqueante.
- No se modificaron la simulación, las entradas sintéticas ni los resultados numéricos.

## [0.1.0] - 2026-07-17

### Added
- Primera simulación DWSIM 9.0.5 del sistema bomba-calefactor.
- Contexto industrial simplificado asociado al lavado de pulpa Kraft.
- Metadatos, supuestos, validación, QC, referencias y procedencia.
- Dataset `process_results_v01.csv`.
- Checksums SHA-256 de la simulación y del dataset.

### Validation
- Balance global de masa: PASS.
- Balance global de energía: PASS.
- Réplica independiente de potencia de bomba: PASS.
- Réplica aproximada de carga térmica: PASS.

### Notes
- Datos sintéticos y didácticos.
- Status inicial: `review`.
