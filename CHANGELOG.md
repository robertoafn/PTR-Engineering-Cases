# Changelog

Todos los cambios notables a este repositorio quedan registrados aquí.

El formato sigue [Keep a Changelog 1.1](https://keepachangelog.com/en/1.1.0/)
y este proyecto adhiere a [Semantic Versioning 2.0.0](https://semver.org/).

## [Unreleased]

### Added
- Caso `001_acondicionamiento_agua_lavado_pulpa_kraft` con simulación DWSIM,
  dataset, metadatos, validación, QA/QC, referencias y procedencia.
- `scripts/preflight.py` como control local único para nomenclatura, metadatos,
  datasets, unidades, checksums, pruebas y linting.
- `AGENTS.md` con reglas persistentes para trabajo local mediante ChatGPT
  Desktop, Codex u otros agentes.
- Soporte opcional de `column` y `primary_key` en sidecars de datasets.
- Pruebas de regresión para objetivos de checksum individuales y validación
  integral de datasets.

### Changed
- README principal reestructurado como activo profesional, con evidencia actual,
  stack demostrado, limitaciones, flujo local y roadmap progresivo.
- Plantilla canónica de casos ampliada para admitir casos básicos o extensos sin
  perder el contrato de trazabilidad.
- `CONTRIBUTING.md` y plantilla de Pull Request sincronizados con el preflight y
  la política de datos.
- GitHub Actions ahora valida los datasets ubicados dentro de `cases/`.
- Validador tabular ampliado para schema, correspondencia columna/símbolo, tipos,
  rangos, nulos, clave primaria y checksum del CSV.
- Estado del Caso 001 actualizado de `review` a `validated` y versión del caso a
  `0.1.1` tras su validación por el autor en DWSIM 9.0.5.

### Fixed
- `compute_checksums.py` ya reconoce correctamente tanto `cases/` como un
  directorio de caso individual y falla ante objetivos vacíos o inexistentes.
- Bloqueadas rutas de artefactos que escapen del directorio del caso.
- Sidecar del Caso 001 alineado con las columnas físicas de
  `process_results_v01.csv` mediante `column`/`symbol`.
- Checksum del sidecar del Caso 001 sincronizado con el CSV versionado.
- Eliminado el falso positivo de CI que validaba `data/processed/` mientras los
  datasets publicados residían dentro de cada caso.

### Validation
- Balance global de masa del Caso 001: PASS.
- Balance global de energía del Caso 001: PASS.
- Verificación independiente de potencia de bombeo: PASS.
- Verificación aproximada de carga térmica: PASS.
- Apertura, resolución e inspección visual del archivo DWSIM por el autor: PASS.
- Workflow `validate` del Pull Request #5: PASS.
- Workflow `lint` del Pull Request #5: PASS.

### Notes
- Los datos del Caso 001 son sintéticos y didácticos.
- No se utilizan datos operacionales reales ni información interna de CMPC.
- La validación actual es del autor y no constituye reproducción externa.
- La exportación del flowsheet a PNG o JPG continúa como mejora visual no
  bloqueante.

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
