# Literature Cases

Esta línea de trabajo transforma casos ya publicados por proyectos académicos
open source en estudios PTR reproducibles. El punto de partida es el corpus
documental de **FOSSEE, IIT Bombay**, pero el corpus completo es una fuente
local de consulta y no forma parte del repositorio.

## Separación entre corpus y casos promovidos

| Zona | Propósito | Política Git |
|---|---|---|
| `C:\PTR-DWSIM-WORK` | Fuentes, investigación y simulaciones locales del mantenedor | Externo; nunca se incorpora en bloque |
| `references/Literature_cases_references/` | Compatibilidad con el corpus histórico | Ignorado; no es el workspace principal |
| `Literature_cases/` | Sólo casos seleccionados y trabajados | Versionado con procedencia, hashes y estado explícito |

Un caso se promueve únicamente cuando:

1. sus archivos fuente se copian sin modificarlos;
2. tamaño y SHA-256 quedan registrados;
3. autoría, licencia, versión y URL se documentan;
4. cualquier discrepancia de fuente queda visible;
5. las variantes nuevas se guardan en rutas diferentes del baseline;
6. los resultados derivados distinguen inspección del estado guardado,
   reconvergencia y validación externa.

## Índice

| ID | Caso | Fuente | Estado |
|---|---|---|---|
| [102](<./102 - Methanol_Water_Distillation_By_Mr_Rahul_A_S/>) | Methanol Water Distillation | FOSSEE DWSIM Flowsheeting Project | `SOURCE_BASELINE_VERIFIED` |

El Caso 102 es el único promovido en el estado versionado actual. La presencia
de otros casos o simulaciones en el workspace local no implica selección,
revisión ni publicación.

## Flujo de trabajo de variantes

`workspace externo → baseline seleccionado inmutable → SimulationRun →
recálculo estable → dataset canónico → benchmark experimental → comparación
de columna → explicación científica → decisión`

Para mezclas alcohol-agua, NRTL, UNIQUAC y Modified UNIFAC Dortmund son modelos
a comparar, no correcciones automáticas. Primero se contrastará el equilibrio
`T-x-y` a presión común con evidencia experimental gobernada; después se
evaluarán purezas, perfiles, deberes térmicos y balances de la columna. DWSIM
9.0.5 permanece como reproducción histórica opcional; el objetivo reproducible
usa la versión estable fijada por la ADR 0001.

## Validación de integridad

```bash
python scripts/validate_literature_case.py Literature_cases/
python scripts/validate_literature_case.py \
  "Literature_cases/102 - Methanol_Water_Distillation_By_Mr_Rahul_A_S" \
  --corpus-case \
  "C:\PTR-DWSIM-WORK\102 - Methanol_Water_Distillation_By_Mr_Rahul_A_S"
```

La segunda forma es local y opcional: CI no contiene el workspace externo. La
ruta exacta puede variar fuera del equipo del mantenedor y nunca se serializa
en manifests canónicos.
