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
1. Completar `validation_spec.yaml` con fronteras, datasets y criterios.
2. `python scripts/validate_case.py cases/NNN_slug --source dataset`
3. `python scripts/validate_case.py cases/NNN_slug --source auto`
4. Abrir `simulations/dwsim/NNN_slug.dwxmz` y ejecutar cuando corresponda.
5. `jupyter nbconvert --execute notebooks/reporting/NN_<slug>.ipynb`
6. `python scripts/preflight.py cases/NNN_slug`

## 9. Resultados
Tabla y figuras clave (SI). Las figuras viven en `assets/figures/`.

## 10. Validación y QC
Ver `validation_spec.yaml`, `validation_report.md` y `qc_checklist.md`.

- `validation_spec.yaml` declara las fronteras, criterios, umbrales y evidencia.
- `validation_results.json` se genera con `--write-artifacts`; no se edita
  manualmente y será la fuente estructurada para visualizaciones.
- `validation_report.md` es el informe técnico canónico. Conservar su narrativa
  y las limitaciones fuera de la sección generada automáticamente.
- Si una métrica no puede recomputarse, marcar `N_A`, `NOT_RUN` o
  `NOT_DEMONSTRATED` con justificación; nunca fabricar un `PASS`.

La validación automática no promueve por sí sola el estado del ciclo de vida.
Consultar `docs/09_validation_protocol.md`.

## 11. Trazabilidad
Ver `provenance.json`.

## 12. Limitaciones
Dominio de validez, supuestos no verificados, sesgos, incertidumbre no
propagada.

## 13. Conclusión técnica
Respuesta al objetivo en lenguaje de ingeniería. Sin marketing.

## 14. Referencias
Ver `references.bib`.
