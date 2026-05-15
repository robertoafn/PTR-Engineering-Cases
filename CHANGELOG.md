# Changelog

Todos los cambios notables a este repositorio quedan registrados aquí.

El formato sigue [Keep a Changelog 1.1](https://keepachangelog.com/en/1.1.0/)
y este proyecto adhiere a [Semantic Versioning 2.0.0](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-05-15

### Added
- Arquitectura fundacional del repositorio PTR Engineering Cases.
- Estructura de carpetas: `docs/`, `templates/`, `schemas/`, `scripts/`,
  `data/`, `simulations/`, `notebooks/`, `dashboards/`, `cases/`,
  `assets/`, `tests/`, `references/`.
- Políticas de gobernanza (codificación, naming, unidades SI, metadata,
  checksums, versioning, lineage, provenance).
- Plantilla canónica de caso reproducible en `templates/case_template/`.
- JSON Schemas: `case_metadata`, `dataset`, `provenance`.
- Vocabularios controlados de unidades y variables.
- Scripts de automatización: `validate_metadata.py`, `validate_tables.py`,
  `compute_checksums.py`, `enforce_naming.py`, `unit_consistency_check.py`.
- Workflow CI `.github/workflows/validate.yml`.
- Plantillas de PR y de Issue (nuevo caso).
- Licencias: MIT (código) y CC BY 4.0 (documentación).
- README profesional, CONTRIBUTING, CODE_OF_CONDUCT, CITATION.cff.
- Configuración Python: `pyproject.toml`, `requirements.txt`, `environment.yml`.

### Notes
- Aún no hay casos reales en `cases/`. Solo el placeholder `000_template`.
- Esta versión es la base sobre la que iterarán futuras releases.

[Unreleased]: https://github.com/robertoafn/PTR-Engineering-Cases/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/robertoafn/PTR-Engineering-Cases/releases/tag/v0.1.0
