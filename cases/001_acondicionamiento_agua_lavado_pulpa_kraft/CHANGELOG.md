# Changelog — 001_acondicionamiento_agua_lavado_pulpa_kraft

## [Unreleased]

### Changed
- Sincronizado el informe de validación con los workflows `validate` y `lint`
  ejecutados satisfactoriamente después de integrar el caso.
- Actualizado el checklist QC para distinguir entre validación automatizada y
  réplica independiente del archivo DWSIM.
- Mantenido el estado `review` hasta documentar la reapertura y resolución desde
  un clon independiente del repositorio.

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
