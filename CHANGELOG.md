# Changelog

Todos los cambios notables a este repositorio quedan registrados aquí.

El formato sigue [Keep a Changelog 1.1](https://keepachangelog.com/en/1.1.0/)
y este proyecto adhiere a [Semantic Versioning 2.0.0](https://semver.org/).

## [Unreleased]

## [0.3.0] - 2026-07-25

### Added
- Caso `003_recuperacion_calor_condensado_y_control_contaminacion_cruzada`, en
  estado `review`, con simulación DWSIM del intercambiador HX-301, resultados
  de proceso, figura de flowsheet, metadatos, procedencia, supuestos,
  checklist QC, informe de validación y referencias.

### Changed
- Actualizados el índice de casos, el resumen técnico y el roadmap del README
  para incorporar el Caso 003 como continuación del condensado residual del
  Caso 002.
- Actualizado `docs/00_overview.md` para reflejar los tres casos integrados y
  el criterio de control hidráulico de contaminación cruzada del Caso 003.
- Separada la validación térmica del Caso 003 de la evaluación de seguridad:
  `P_limpio - P_contaminado = 0 Pa` se documenta como condición sin margen,
  no como demostración de control operacional.
- Los sidecars de datasets ahora enlazan cada símbolo científico con su columna
  CSV mediante el campo `column`, documentan todas las columnas canónicas y
  declaran su clave primaria.
- Añadidos `scripts/preflight.py` y `requirements-ci.txt` para un control local
  único y un entorno mínimo de gobernanza en GitHub Actions.
- Eliminadas las referencias corporativas y documentada la ubicación
  conceptual de cada caso dentro de una cadena productiva Kraft genérica.
- Sincronizadas las versiones de los casos 001, 002 y 003 como `0.1.2`,
  `0.1.1` y `0.1.1`, respectivamente, junto con sus datasets modificados.

### Fixed
- `compute_checksums.py` ahora verifica correctamente una ruta de caso
  individual y falla ante rutas sin `provenance.json`.
- `unit_consistency_check.py` valida los campos `unit` reales de entradas y
  salidas de `metadata.yaml`.
- CI valida los datasets canónicos bajo `cases/`; una ejecución con cero
  datasets deja de producir un falso positivo.
- Sincronizado el checksum obsoleto del sidecar de resultados del Caso 001 con
  el CSV y su `provenance.json`.
- Corregido el flujo de energía derivado de `MSTR-303` en el dataset del Caso
  003 para que sea consistente con caudal y entalpía específica publicados.

### Validation
- Preflight integral aprobado para los tres casos.
- 3 metadatos y 4 datasets canónicos validados.
- Unidades verificadas en 7 archivos y checksums SHA-256 conformes.
- 28 pruebas automatizadas y Ruff: PASS.

## [0.2.0] - 2026-07-18

### Added
- Caso `001_acondicionamiento_agua_lavado_pulpa_kraft`, validado, con
  simulación DWSIM, dataset, validación, QC y trazabilidad.
- Caso `002_recuperacion_vapor_flash_y_particion_de_volatiles`, en estado
  `review`, con simulación flash agua-metanol, cromatografía GC-FID sintética,
  resultados, validación, QC y procedencia.
- Figura exportada del flowsheet DWSIM del Caso 001.

### Changed
- Actualizadas la portada, el índice de casos, el roadmap y el overview para
  reflejar un portafolio con dos casos integrados.
- Estado del Caso 001 actualizado de `review` a `validated`; versión del caso
  actualizada de `0.1.0` a `0.1.1`.
- Registrada la reapertura, resolución e inspección visual del Caso 001 en
  DWSIM 9.0.5, junto con la procedencia de su figura.

### Validation
- Controles de masa, energía, unidades, metadatos, naming y checksums de los
  casos publicados: PASS.

### Notes
- Los datos y cromatogramas de los casos 001 y 002 son sintéticos y no
  representan condiciones operacionales ni información de una instalación
  industrial específica.

## [0.1.0] - 2026-05-15

### Added
- Arquitectura fundacional del repositorio PTR Engineering Cases.
- Estructura de carpetas: `docs/`, `templates/`, `schemas/`, `scripts/`,
  `data/`, `simulations/`, `notebooks/`, `dashboards/`, `cases/`,
  `assets/`, `tests/`, `references/`.
- Políticas de gobernanza: codificación, naming, unidades SI, metadata,
  checksums, versioning, lineage y provenance.
- Plantilla canónica de caso reproducible en `templates/case_template/`.
- JSON Schemas: `case_metadata`, `dataset` y `provenance`.
- Vocabularios controlados de unidades y variables.
- Scripts de automatización: `validate_metadata.py`, `validate_tables.py`,
  `compute_checksums.py`, `enforce_naming.py` y
  `unit_consistency_check.py`.
- Workflow CI `.github/workflows/validate.yml`.
- Plantillas de Pull Request y de Issue para nuevos casos.
- Licencias MIT para código y CC BY 4.0 para documentación.
- Archivos principales: `README.md`, `CONTRIBUTING.md`,
  `CODE_OF_CONDUCT.md` y `CITATION.cff`.
- Configuración Python mediante `pyproject.toml`, `requirements.txt`
  y `environment.yml`.

### Notes
- En esta versión todavía no existían casos implementados en `cases/`.
- Solo se incluía el placeholder `000_template`.
- Esta versión constituye la arquitectura base para las iteraciones posteriores.

[Unreleased]: https://github.com/robertoafn/PTR-Engineering-Cases/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/robertoafn/PTR-Engineering-Cases/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/robertoafn/PTR-Engineering-Cases/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/robertoafn/PTR-Engineering-Cases/releases/tag/v0.1.0
