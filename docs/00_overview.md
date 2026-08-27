# 00 — Overview

## Propósito

**Periodic Table Research — From Elements to Industrial Decisions** construye
un ecosistema interoperable de casos científicos e industriales de ingeniería
química. El repositorio conserva la reproducibilidad como unidad mínima de
trabajo y amplía su cadena conceptual:

> elementos → sustancias → propiedades → fenómenos → modelos → simulación →
> evidencia experimental → proceso → energía → ambiente → economía →
> supply chain → decisión industrial

El valor de un caso no depende de cuántos archivos contiene, sino de cuánto
conocimiento verificable deja disponible para otros casos.

## Estado actual

La fundación técnica está implementada:

- políticas FAIR, SI, IUPAC, QC, metrología y versionado;
- schemas para casos, datasets, procedencia, validación y ejecuciones;
- validadores, pruebas y CI;
- cuatro casos PTR con estados conservados según su evidencia;
- una línea de Literature Cases con fuente inmutable y promoción selectiva;
- dashboard científico Streamlit;
- contrato `SimulationRun` y política de versiones DWSIM.

El repositorio se encuentra en transición hacia datos y entidades
interoperables. Esta transición no significa que todas sus capas objetivo estén
disponibles:

| Capacidad | Estado |
|---|---|
| DWSIM, Python, DWSIM API, schemas, QC, provenance y Streamlit | Implementada |
| Caso 102: fuente FOSSEE y registro de inspección | Implementada |
| Caso 102: réplicas 10.2.0 y VLE de Álvarez et al. | Contexto local en revisión |
| Dataset experimental canónico y recálculos estables del Caso 102 | Pendiente |
| SQL analítico, modelo estrella y Power BI | Planificado |
| JSON-LD, Knowledge Graph y PTR Industrial Decision Core | Planificado |

La dirección normativa y sus gates están en
[12 — Estado y dirección del proyecto](12_project_direction.md).

## Líneas de publicación

1. **Casos PTR (`cases/`)**: problemas desarrollados dentro del proyecto con
   modelo, evidencia, validación y procedencia propios. El alcance de 001–004
   está cerrado; sus estados no se homogeneizan:

   - 001: `validated/PASS`;
   - 002: `review/FAIL`;
   - 003 y 004: `review/CONDITIONAL`.

2. **Casos de literatura (`Literature_cases/`)**: fuentes externas
   seleccionadas y sus derivados auditables. La incorporación de una fuente
   verifica identidad, licencia, integridad y procedencia; no implica
   reconvergencia ni validación científica.

El espacio externo del mantenedor es `C:\PTR-DWSIM-WORK`. No forma parte del
repositorio ni es una dependencia de CI. Sólo se promueven artefactos aptos,
seleccionados y gobernados. La ruta interna
`references/Literature_cases_references/` se conserva ignorada únicamente por
compatibilidad con el flujo histórico.

## Arquitectura por capas

| Capa | Responsabilidad | Autoridad |
|---|---|---|
| Contexto de investigación | Fuentes, simulaciones exploratorias y notas locales | No canónica; fuera de Git |
| Fuente promovida | Original identificado, licenciable e inmutable | Hash, manifiesto y provenance |
| Ejecución | Configuración y actividad DWSIM explícita | `SimulationRun` |
| Dato canónico | Observaciones y resultados normalizados | Dataset versionado + sidecar |
| Validación | Reglas, métricas, dominio y veredicto | `validation_spec` + `validation_results` |
| Analítica | Figuras, Streamlit y futuras vistas SQL/Power BI | Derivada; nunca reemplaza al dato canónico |
| Semántica | IDs compartidos y futuras vistas JSON-LD/Knowledge Graph | Derivada de contratos versionados |
| Decisión | Alternativas, restricciones, energía, ambiente y economía | Sólo después de evidencia y validación suficientes |

Las capas superiores pueden recomputarse desde las inferiores. Una vista no
debe introducir hechos que no existan en la evidencia gobernada.

## Evidencia

`SimulationRun` separa dos ejes:

- modo de evidencia: experimental, calculated, simulated, estimated o
  documentary;
- origen del dato: empirical, literature, synthetic o hypothetical.

El schema de datasets conserva temporalmente el campo legado `source_type`.
Hasta que exista una migración compatible, no debe afirmarse que todos los
datasets implementan ya ambos ejes.

Integridad, convergencia, paridad, validación científica, aptitud industrial y
decisión son estados diferentes. Cada afirmación debe identificar la evidencia
que la respalda y las limitaciones que todavía impiden promoverla.

## Caso piloto 102

El Caso 102, *Methanol–Water Distillation*, es el primer piloto de extremo a
extremo. El baseline FOSSEE y su inspección están gobernados. Las cuatro
réplicas 10.2.0 del autor y la transcripción preliminar de VLE permanecen fuera
de Git como contexto en revisión.

El siguiente bloque científico es:

1. resolver derechos, unidades y segunda revisión del dataset experimental;
2. recalcular desde inicio limpio en la versión estable fijada por ADR 0001;
3. comparar Raoult, NRTL, UNIQUAC y Modified UNIFAC Dortmund mediante un
   benchmark `T-x-y` a presión común;
4. comparar después la columna completa;
5. extender el caso hacia energía, CAPEX, GHG y decisión sólo con la base
   científica ya validada.

DWSIM 9.0.5 conserva el rol histórico `reference_reproduction`, pero no
bloquea la línea `target_reproducible`.

## Exclusiones y límites

- No se publican datos reales o fuentes de terceros sin derechos compatibles.
- No se presenta material local no revisado como dataset canónico.
- No se deduce convergencia desde un estado guardado.
- No se presenta una réplica del autor como reproducción independiente.
- No se describe una tecnología planificada como capacidad implementada.
- Los casos PTR no representan una planta industrial integrada ni condiciones
  operacionales de una instalación específica.

Las reglas operativas para agentes están en [`AGENTS.md`](../AGENTS.md); la
metodología y gobernanza continúan en
[`docs/01_methodology.md`](01_methodology.md) y
[`docs/02_governance.md`](02_governance.md).
