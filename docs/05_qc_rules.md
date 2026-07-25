# 05 — Reglas de QC

Reglas automáticas aplicadas en CI a cada PR.

| # | Regla | Verificación | Script |
|---|---|---|---|
| 1 | Schema validation | `metadata.yaml` y sidecars de datasets contra JSON Schema | `validate_metadata.py`, `validate_tables.py` |
| 2 | Uniqueness | Par (`case_id`, `dataset_id`) y clave primaria declarada sin duplicados | `validate_tables.py` |
| 3 | Completeness | Columnas declaradas y valores obligatorios no nulos | `validate_tables.py` |
| 4 | Type/range validation | Tipo declarado y rangos definidos en cada sidecar | `validate_tables.py` |
| 5 | Null control | Política `nullable` explícita por columna | schema |
| 6 | Referential integrity | `case_id` del sidecar coincide con el caso que lo contiene | `validate_tables.py` |
| 7 | File naming | Regex contra Sección 3 | `enforce_naming.py` |
| 8 | Unit consistency | Vocabulario SI controlado | `unit_consistency_check.py` |
| 9 | Metadata completeness | 20 campos del caso presentes | `validate_metadata.py` |
| 10 | Checksum verification | SHA-256 recomputado == declarado | `compute_checksums.py --verify` |

## Veredicto
Una sola regla en `FAIL` impide elevar el estado del caso por encima de
`review`.

`validate_tables.py` inspecciona únicamente datasets canónicos con un sidecar
adyacente `<dataset>.meta.yaml`; los archivos crudos y exportaciones auxiliares
se preservan como evidencia, pero no se interpretan como tablas canónicas. El
campo `column` del sidecar enlaza el símbolo científico con el encabezado real
del CSV.
