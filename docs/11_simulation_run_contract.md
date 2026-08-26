# 11 — Contrato `SimulationRun`

## Propósito

`SimulationRun` es el registro inmutable de una inspección o ejecución de
simulación. Une caso, escenario, software, configuración termodinámica,
artefactos, evidencia y procedencia sin convertir el archivo DWSIM en la
fuente directa del dashboard.

El contrato implementa la cadena mínima:

> Case → Scenario → SimulationRun → Artifact → Observation / Validation

El schema normativo es
[`schemas/simulation_run.schema.json`](../schemas/simulation_run.schema.json).
Este primer corte no migra los casos existentes ni promueve archivos desde
`C:\PTR-DWSIM-WORK`.

## Qué registra y qué no demuestra

Un `SimulationRun` registra hechos de ejecución. No demuestra por sí solo
paridad, exactitud, robustez ni aptitud industrial.

| Campo | Pregunta que responde | No debe interpretarse como |
|---|---|---|
| `status` | ¿Terminó la actividad registrada? | Veredicto científico |
| `execution.convergence_status` | ¿Qué evidencia existe sobre convergencia? | Acuerdo con datos externos |
| `version_role` | ¿Qué función cumple esta versión? | Orden cronológico o calidad automática |
| `evidence.evidence_mode` | ¿Cómo se obtuvo la observación? | Origen del sistema o dataset |
| `evidence.data_origin` | ¿De dónde procede el caso o dato? | Método de obtención |
| `validation_result_ids` | ¿Qué resultados de validación lo evalúan? | Validación implícita por estar presente |

`NOT_RUN` pertenece a un gate o especificación de validación. Si una
simulación nunca se ejecutó no se fabrica un `SimulationRun` completado para
representarla.

## Campos obligatorios

| Grupo | Contenido mínimo |
|---|---|
| Identidad | `schema_version`, `run_id`, `case_id`, `scenario_id`, `run_type` |
| Clasificación | `version_role`, `status`, `recorded_at_utc` |
| Software | nombre, versión y canal de release; build, label y edición cuando existan |
| Modelo | paquete termodinámico, modelo de entalpía y parameter set trazable |
| Artefactos | ID, ruta relativa al repositorio, función, SHA-256 e inmutabilidad |
| Ejecución | modo, indicador de recálculo, inicio limpio y estado de convergencia |
| Evidencia | `evidence_mode`, `data_origin` y fuentes |
| Procedencia | actividad, agentes, artefactos usados/generados y corridas de origen |

Los identificadores son estables y legibles por máquina. Se recomienda el
prefijo semántico `run:`, `scenario:`, `artifact:`, `activity:`, `agent:` o
`source:` según corresponda.

## Roles de versión

La versión numérica no define el uso de una corrida. El campo
`version_role` adopta uno de estos valores:

| Valor | Significado |
|---|---|
| `source_baseline` | Original histórico preservado; puede ser sólo inspeccionado |
| `reference_reproduction` | Reproducción deliberada de una referencia declarada |
| `exploratory_migration` | Ensayo de compatibilidad o diagnóstico sin autoridad de validación |
| `target_reproducible` | Corrida estable candidata a evidencia canónica reproducible |

La asignación vigente para DWSIM se decide en
[ADR 0001 — Política de versiones DWSIM](adr/0001-dwsim-version-policy.md).

## Modos de ejecución y convergencia

### `saved_state_inspection`

Representa lectura de un estado serializado sin recalcular. Debe declarar:

- `recalculated = false`;
- `clean_start = false`;
- `convergence_status = saved_state_only`.

Un indicador guardado, un valor numérico presente o un mensaje histórico no
se promueven a `reported_success` ni a `verified_converged`.

### `manual_gui`

Registra una ejecución interactiva. Puede ser reproducible si conserva
entrada y salida separadas, tiempos, configuración completa, resultados y
hashes. El nombre del operador se referencia mediante `agent_ids`.

### `automation_api`

Registra una ejecución automatizada. Debe referenciar el script o herramienta
usada como artefacto o agente de software y conservar los logs disponibles.
Automatización mejora repetibilidad, pero no sustituye la validación.

Los estados de convergencia se interpretan así:

| Estado | Significado |
|---|---|
| `saved_state_only` | Sólo se inspeccionó el estado serializado |
| `reported_success` | El simulador informó éxito, aún sin verificación completa |
| `verified_converged` | Se verificaron solución, mensajes y controles numéricos definidos |
| `failed` | La ejecución no convergió o terminó con error |
| `unknown` | La evidencia disponible no permite clasificarla |

## Separación epistemológica

PTR Core requiere dos ejes independientes:

- `evidence_mode`: `experimental`, `calculated`, `simulated`, `estimated` o
  `documentary`;
- `data_origin`: `empirical`, `literature`, `synthetic` o `hypothetical`.

Por ejemplo, una corrida DWSIM sobre el Caso 102 puede ser evidencia
`simulated` con origen `literature`. Una inspección XML del original es
evidencia `documentary` con origen `literature`. Ninguna combinación
autoriza por sí misma un veredicto `PASS`.

## Gate de `target_reproducible`

El schema impide etiquetar como objetivo reproducible una corrida que no
cumpla, como mínimo:

1. canal de software `stable` y versión fijada por una ADR;
2. actividad `completed`, con inicio y fin UTC;
3. recálculo real desde inicio limpio;
4. `verified_converged`;
5. package termodinámico, modelo de entalpía y procedencia de parámetros sin
   estado `missing`;
6. artefactos separados para entrada, salida y dataset de resultados;
7. rutas internas al repositorio, hashes SHA-256 en minúsculas y
   `immutable = true`;
8. evidencia clasificada como `simulated`.

Este gate alcanza reproducibilidad estructural (DR2). La promoción a
validación y robustez (DR3) sigue requiriendo `validation_spec`, métricas,
dominio, tolerancias, datos externos cuando correspondan y un
`validation_result` independiente.

## Parámetros termodinámicos

`parameter_set.provenance_status` distingue:

- `software_builtin`: parámetros distribuidos por el software;
- `documented_external`: parámetros de una fuente identificada;
- `estimated_by_software`: estimación automática declarada;
- `not_applicable`: el modelo no utiliza ese tipo de parameter set;
- `missing`: procedencia aún no resuelta.

Los tres primeros estados requieren una fuente y un
`values_artifact_id`. El artefacto puede ser una tabla de parámetros o una
entrada DWSIM inmutable que los contenga. `auto_estimated = true` sólo es
válido con `estimated_by_software`.

Para comparar modelos, un cambio de parameter set o de modelo de entalpía
obliga a crear otro `run_id`; no se modifica el registro previo.

## Artefactos y procedencia

Las rutas deben usar `/`, ser relativas a la raíz Git y no contener `..`,
URI ni unidades de Windows. Un manifiesto canónico nunca apunta directamente
a una ruta local externa.

La correspondencia PROV-lite es:

| `SimulationRun` | PROV-lite |
|---|---|
| `provenance.activity_id` | activity |
| `provenance.agent_ids` | agents |
| elementos de `artifacts` | entities |
| `used_artifact_ids` | used |
| `generated_artifact_ids` | generated |
| `derived_from_run_ids` | lineage entre actividades/corridas |

## Autoría y validación independiente

`provenance.agent_ids` identifica quién ejecutó, inspeccionó o automatizó la
actividad; no convierte esa actividad en validación independiente. Una réplica
realizada por su propio autor se registra como tal y puede aportar evidencia de
reproducibilidad del autor, pero no debe describirse como reproducción externa.

Los resultados de validación posteriores deben identificar por separado al
autor de la simulación y al agente evaluador. Si ambos coinciden, el veredicto
se etiqueta como validación del autor. La independencia sólo puede afirmarse
cuando el agente evaluador, el procedimiento y los artefactos usados permiten
demostrarla explícitamente.

JSON Schema valida forma, enums y gates locales. La coherencia referencial
entre IDs, existencia de archivos, hashes, orden temporal y balances debe
comprobarse con validadores de repositorio antes de una promoción.

## Ubicación recomendada

Para nuevas promociones:

```text
Literature_cases/<case>/runs/<run_id>/
├── simulation_run.json
├── input.dwxmz
├── output.dwxmz
├── results.csv
└── run.log                 # si está disponible
```

Los originales históricos permanecen en su ubicación actual y se referencian
por ruta; no se mueven para satisfacer esta convención. Las carpetas
`variants/` existentes se migrarán sólo cuando haya una corrida real que
registrar.

## Ejemplo y evolución

La fixture
[`tests/fixtures/simulation_run_valid.json`](../tests/fixtures/simulation_run_valid.json)
es sintética y sólo demuestra la estructura de un objetivo reproducible; no
es evidencia de un caso publicado.

`schema_version = 1.0.0` identifica este contrato. Un cambio incompatible
requiere nueva versión del schema, migración explícita y entrada en el
changelog; nunca una reinterpretación silenciosa de registros existentes.
