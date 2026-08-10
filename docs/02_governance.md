# 02 — Gobernanza de Datos

## Líneas de publicación

| Línea | Ubicación versionada | Regla de ingreso |
|---|---|---|
| Casos PTR | `cases/` | Modelo, datos, validación y procedencia propios |
| Casos de literatura | `Literature_cases/` | Promoción selectiva de una fuente identificada y sus derivados auditables |

El corpus FOSSEE de trabajo reside en
`references/Literature_cases_references/`. Es una fuente local de exploración,
está excluida por `.gitignore` y no forma parte del contenido publicable del
repositorio. No se debe usar `git add -f` para incorporar archivos desde esa
ruta.

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
- En un caso de literatura, los originales se enumeran además en
  `source_manifest.json` y `checksums.sha256` con ruta, tamaño e indicador de
  inmutabilidad.

## Versioning
- **SemVer** (`MAJOR.MINOR.PATCH`).
- Tags Git por release.
- Cambios en `CHANGELOG.md` (Keep a Changelog).

## Lineage
Cada artefacto declara `derived_from: [<dataset_id>@<version>]`.

## Provenance
Modelo W3C PROV-lite implementado en `provenance.json` con `agents`,
`activities` y `entities`. Esquema: `schemas/provenance.schema.json`.

## Inmutabilidad y variantes de literatura

- Un archivo fuente promovido desde FOSSEE se conserva byte a byte; su hash es
  la identidad auditable del artefacto.
- La versión declarada en la ficha FOSSEE y la versión interna que pueda
  contener el archivo se registran por separado cuando difieren.
- Una reproducción en DWSIM 9.0.5 o con otro paquete termodinámico se almacena
  como variante y nunca reemplaza al original.
- Las variantes que aporte el usuario deben declarar software, paquete,
  parámetros, autoría, fecha, relación con la fuente y hashes propios.
- La verificación de integridad, la convergencia, la paridad numérica y la
  validación científica son estados distintos; ninguno se infiere de otro.
