# Literature Cases

Esta línea de trabajo transforma casos ya publicados por proyectos académicos
open source en estudios PTR reproducibles. El punto de partida es el corpus
documental de **FOSSEE, IIT Bombay**, pero el corpus completo es una fuente
local de consulta y no forma parte del repositorio.

## Separación entre corpus y casos promovidos

| Zona | Propósito | Política Git |
|---|---|---|
| `references/Literature_cases_references/` | Corpus local FOSSEE sin curar | Ignorado de forma completa por `.gitignore` |
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

El Caso 102 es el único promovido en este release. La presencia de otros casos
en el corpus local no implica selección, revisión ni publicación.

## Flujo de trabajo de variantes

`baseline FOSSEE inmutable → paridad DWSIM 9.0.5 con el mismo paquete → modelo
termodinámico alternativo justificado → comparación cuantitativa → explicación
científica`

Para mezclas alcohol-agua, NRTL o UNIQUAC son candidatos razonables, pero no se
presentan como corrección automática. Primero debe comprobarse la paridad con
Raoult y luego contrastar equilibrio vapor-líquido, purezas, perfiles, deberes
térmicos y balances frente a evidencia trazable.

## Validación de integridad

```bash
python scripts/validate_literature_case.py Literature_cases/
python scripts/validate_literature_case.py \
  "Literature_cases/102 - Methanol_Water_Distillation_By_Mr_Rahul_A_S" \
  --corpus-case \
  "references/Literature_cases_references/DWSIM - FOSSEE/Flowsheeting Project/102 - Methanol_Water_Distillation_By_Mr_Rahul_A_S"
```

La segunda forma es local y opcional: CI no contiene el corpus ignorado.
