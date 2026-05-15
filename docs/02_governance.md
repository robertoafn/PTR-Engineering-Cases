# 02 — Gobernanza de Datos

## Codificación
- **UTF-8 sin BOM** para todo archivo de texto.
- Salto de línea **LF** (fijado en `.gitattributes`).

## Separadores y decimales (CSV)
| Aspecto | Regla |
|---|---|
| Separador de columnas | `,` |
| Separador decimal | `.` |
| Separador de miles | ninguno |
| Notación científica | `e` minúscula (`1.013e5`) |

## Fechas
- ISO 8601, UTC, con sufijo `Z`. Ejemplo: `2026-05-15T12:34:56Z`.

## Metadatos obligatorios por dataset
`dataset_id`, `case_id`, `title`, `description`, `source_type`
(`synthetic|hypothetical|literature|simulated`), `units`, `variables`,
`created_at`, `author`, `license`, `version`, `checksum_sha256`,
`provenance_ref`.

## Checksums
- Algoritmo: **SHA-256**.
- Almacenado en `provenance.json` por caso.
- Recalculable con `scripts/compute_checksums.py`.

## Versioning
- **SemVer** (`MAJOR.MINOR.PATCH`).
- Tags Git por release.
- Cambios en `CHANGELOG.md` (Keep a Changelog).

## Lineage
Cada artefacto declara `derived_from: [<dataset_id>@<version>]`.

## Provenance
Modelo W3C PROV-lite implementado en `provenance.json` con `agents`,
`activities` y `entities`. Esquema: `schemas/provenance.schema.json`.
