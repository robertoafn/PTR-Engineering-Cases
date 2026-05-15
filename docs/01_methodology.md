# 01 — Metodología

Cada caso del repositorio respeta la secuencia metodológica obligatoria:

```
fenómeno
  → fundamento científico
    → modelo
      → simulación / procesamiento
        → resultados
          → validación / QC
            → trazabilidad
              → conclusión técnica
```

## Etapas

| Etapa | Artefacto principal | Verificación |
|---|---|---|
| Fenómeno | Sección 1 del README del caso | Revisión humana |
| Fundamento científico | Sección 2 + `references.bib` | Citas con DOI |
| Modelo | Sección 4 + `assumptions.md` | Revisión humana |
| Simulación / procesamiento | `simulations/` o `notebooks/reporting/` | Ejecución end-to-end |
| Resultados | Tablas + figuras en `assets/` | QC tabular |
| Validación / QC | `validation_report.md` | Métricas y veredicto |
| Trazabilidad | `provenance.json` + checksums | `compute_checksums.py --verify` |
| Conclusión técnica | Sección 13 del README del caso | Revisión humana |

## Principios

1. Reproducibilidad sobre espectacularidad.
2. Unidades SI obligatorias.
3. Datos sintéticos/hipotéticos etiquetados explícitamente.
4. Software con versión declarada.
5. Cada artefacto con SHA-256.
