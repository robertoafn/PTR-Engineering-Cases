# 01 — Metodología

La versión 0.6.0 mantiene dos flujos de trabajo. Los casos PTR desarrollan un
problema propio en `cases/`; los casos de literatura parten de un artefacto
publicado por terceros y sólo se promueven selectivamente a
`Literature_cases/`. Ambos flujos respetan la secuencia metodológica:

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
6. Un estado documental o de integridad no se presenta como validación
   científica ni como reconvergencia de una simulación.

## Flujo de casos PTR

Los casos 001–004 conservan su modelo, evidencia, validación y procedencia en
`cases/`. En v0.6.0 se cierra su alcance de desarrollo, pero sus estados siguen
la evidencia disponible: 001 es `validated/PASS`; 002 es `review/FAIL`; 003 y
004 son `review/CONDITIONAL`. Un cambio de estado exige regenerar los resultados
y documentar el criterio que lo sustenta.

## Flujo de casos de literatura

1. Explorar el corpus únicamente en
   `references/Literature_cases_references/`. Esta carpeta es local, está
   ignorada por Git y no se publica en bloque.
2. Seleccionar un caso y crear su directorio en `Literature_cases/`; v0.6.0
   comienza con el Caso 102 de FOSSEE.
3. Copiar sólo los artefactos fuente necesarios. Se declaran inmutables: no se
   regraban, convierten ni sobrescriben.
4. Registrar nombre, tamaño y SHA-256 en `source_manifest.json` y
   `checksums.sha256`; documentar fuente, versión declarada, licencia y
   discrepancias en `metadata.yaml`, `provenance.json` y el informe.
5. Verificar la promoción con:

   ```bash
   python scripts/validate_literature_case.py "Literature_cases/102 - Methanol_Water_Distillation_By_Mr_Rahul_A_S"
   ```

   Cuando el corpus local está disponible, se añade `--corpus-case` para
   comprobar igualdad binaria con el origen. El resultado acredita integridad
   de los archivos, no la corrección termodinámica del modelo.
6. Incorporar reproducciones nuevas en un subdirectorio de variantes. Para el
   Caso 102, el usuario aportará primero la reproducción en DWSIM 9.0.5; otras
   configuraciones, como un paquete NRTL, se mantendrán separadas y deberán
   declarar versión, supuestos y resultados propios.
7. Comparar fuente y variantes mediante métricas reproducibles. Sólo entonces
   se actualiza el estado científico del caso y, si existe evidencia suficiente,
   se incorpora al dashboard.

Los metadatos, informes y figuras derivados pueden evolucionar. Los binarios
marcados como originales no cambian: cualquier corrección genera una variante
nueva con procedencia independiente.
