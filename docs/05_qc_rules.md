# 05 — Reglas de QC

Reglas automáticas aplicadas en CI a cada PR.

| # | Regla | Verificación | Script |
|---|---|---|---|
| 1 | Schema validation | `metadata.yaml` y datasets contra JSON Schema | `validate_metadata.py`, `validate_tables.py` |
| 2 | Uniqueness | `case_id`, `dataset_id`, claves primarias | `validate_tables.py` |
| 3 | Completeness | Campos obligatorios no nulos | `validate_tables.py` |
| 4 | Range validation | T>0 K, P>0 Pa, fracciones ∈ [0,1] | `validate_tables.py` |
| 5 | Null control | Política `nullable` explícita por columna | schema |
| 6 | Referential integrity | FK entre tablas | `validate_tables.py` |
| 7 | File naming | Regex contra Sección 3 | `enforce_naming.py` |
| 8 | Unit consistency | Vocabulario SI controlado | `unit_consistency_check.py` |
| 9 | Metadata completeness | 20 campos del caso presentes | `validate_metadata.py` |
| 10 | Checksum verification | SHA-256 recomputado == declarado | `compute_checksums.py --verify` |

## Veredicto
Una sola regla en `FAIL` impide elevar el estado del caso por encima de
`review`.
