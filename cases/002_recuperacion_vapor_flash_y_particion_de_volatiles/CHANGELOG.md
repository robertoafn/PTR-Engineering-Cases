# Changelog

All notable changes to this case will be documented in this file.

## [Unreleased]

## [0.1.2] - 2026-07-25

### Added

- Especificación declarativa `validation_spec.yaml`, resultado estructurado
  `validation_results.json` y sección automática del informe.

### Validation

- Balances globales de masa, metanol y energía, isoentalpía, partición,
  controles GC-FID, unidades y checksums: `PASS`.
- Paridad energética DWSIM API-dataset: `FAIL`; la desviación máxima es
  `0.115554596249 %` en `MSTR-204_LIQUIDO_FLASH`, sobre el umbral de `0.05 %`.
- El caso permanece en `review`; no se modificaron la simulación ni los datos
  durante la validación.

## [0.1.1] - 2026-07-25

### Changed

- Los sidecars de resultados de proceso y cromatografía ahora documentan las
  columnas canónicas, tipos, unidades y claves primarias; ambos datasets
  avanzan a `0.1.1`.
- Precisada la ubicación del flash de condensado dentro de una cadena Kraft
  genérica y su relación conceptual con el Caso 003.
- Eliminadas las referencias corporativas.
- Versión del caso actualizada de `0.1.0` a `0.1.1`.

## [0.1.0] - 2026-07-18

### Added

- Archivo DWSIM del escenario flash agua-metanol con válvula y separador.
- Exportación de resultados DWSIM, flowsheet y evidencia visual.
- Cromatogramas sintéticos, archivo OpenChrom nativo para `OC-MSTR-203` y reporte de pico.
- Reconstrucción externa y trazable de áreas trapezoidales por la limitación documentada de integración FID.
- Metadatos, datasets canónicos, supuestos, checklist QC, informe de validación y procedencia inicial.
