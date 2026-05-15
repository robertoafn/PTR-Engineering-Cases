# NNN_slug — <title>

> **Status:** draft | review | validated | published
> **Versión:** 0.1.0
> **Aviso de datos:** declarar `source_type` en `metadata.yaml`
> (`synthetic` / `hypothetical` / `simulated` / `literature`).

---

## 1. Fenómeno
Descripción técnica del fenómeno físico/químico abordado. Indicar escala
(laboratorio, planta piloto, industrial-simulada) y régimen (estacionario,
transitorio, isotermo, etc.).

## 2. Objetivo
Pregunta de ingeniería única y verificable.

> Determinar X con criterio de aceptación Y, en el dominio Z.

## 3. Fundamento científico
Marco teórico mínimo: ecuaciones, leyes aplicadas, supuestos termodinámicos
o cinéticos, regímenes de validez. Citar fuentes en `references.bib`.

## 4. Modelo de ingeniería
Modelo concreto (p. ej. Peng-Robinson + NRTL, balance global, LMTD, ε-NTU).
Justificar elección frente a alternativas.

## 5. Supuestos
Ver `assumptions.md`.

## 6. Stack y versiones
| Componente | Versión | Licencia | Propósito |
|---|---|---|---|
| DWSIM | x.y.z | GPL-3.0 | Simulación de proceso |
| Python | 3.12 | PSF | Análisis y QC |

## 7. Entradas
Ver `metadata.yaml > inputs`.

## 8. Procedimiento reproducible
1. `python scripts/validate_metadata.py cases/NNN_slug`
2. Abrir `simulations/dwsim/NNN_slug.dwxmz` y ejecutar.
3. `jupyter nbconvert --execute notebooks/reporting/NN_<slug>.ipynb`
4. `python scripts/compute_checksums.py cases/NNN_slug`

## 9. Resultados
Tabla y figuras clave (SI). Las figuras viven en `assets/figures/`.

## 10. Validación y QC
Ver `validation_report.md` y `qc_checklist.md`.

## 11. Trazabilidad
Ver `provenance.json`.

## 12. Limitaciones
Dominio de validez, supuestos no verificados, sesgos, incertidumbre no
propagada.

## 13. Conclusión técnica
Respuesta al objetivo en lenguaje de ingeniería. Sin marketing.

## 14. Referencias
Ver `references.bib`.
