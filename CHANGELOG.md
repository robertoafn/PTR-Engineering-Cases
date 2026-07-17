# Changelog

Todos los cambios notables a este repositorio quedan registrados aquí.

El formato sigue [Keep a Changelog 1.1](https://keepachangelog.com/en/1.1.0/)
y este proyecto adhiere a [Semantic Versioning 2.0.0](https://semver.org/).

## [Unreleased]

### Added
- Caso `001_acondicionamiento_agua_lavado_pulpa_kraft`.
- Simulación estacionaria desarrollada en DWSIM 9.0.5.
- Modelo simplificado de bombeo y calentamiento de agua asociado
  conceptualmente al lavado de pulpa Kraft.
- Archivo reproducible de simulación DWSIM en formato `.dwxmz`.
- Contexto científico e industrial del proceso.
- Fundamentos de balance de masa, balance de energía, bombeo y calentamiento.
- Metadatos estructurados en `metadata.yaml`.
- Registro de supuestos y limitaciones en `assumptions.md`.
- Dataset de resultados simulados y su archivo de metadatos.
- Informe de validación de balances y comprobaciones independientes.
- Lista de control de calidad y reproducibilidad.
- Registro de procedencia y checksums SHA-256.
- Referencias técnicas y documentación del caso.
- Changelog independiente para el Caso 001.

### Validation
- Balance global de masa: PASS.
- Balance global de energía: PASS.
- Verificación independiente de la potencia de bombeo: PASS.
- Verificación aproximada de la carga térmica: PASS.
- Consistencia de las condiciones de entrada y salida: PASS.
- Estado físico líquido de las corrientes: PASS.

### Notes
- Los datos del Caso 001 son sintéticos y didácticos.
- El caso no contiene datos operacionales reales ni información interna de CMPC.
- El modelo representa un sistema auxiliar simplificado y no un lavador de pulpa completo.
- El Caso 001 permanece con estado `review` hasta completar las validaciones
  locales, la reapertura desde el repositorio versionado y la ejecución satisfactoria
  del workflow de integración continua.

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

[Unreleased]: https://github.com/robertoafn/PTR-Engineering-Cases/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/robertoafn/PTR-Engineering-Cases/releases/tag/v0.1.0
