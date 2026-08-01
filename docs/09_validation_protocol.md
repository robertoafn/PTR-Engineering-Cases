# 09 — Protocolo de validación automatizada

## Propósito

El motor de validación PTR transforma las fronteras físicas, los criterios de
aceptación y sus evidencias en controles declarativos y reproducibles. Cada caso
define su contrato en `validation_spec.yaml`; el código del motor permanece
genérico y no contiene condicionales asociados a IDs concretos.

Este protocolo complementa la [política de validación](./06_validation_policy.md).
Un resultado automático describe la evidencia disponible, pero no cambia por sí
solo el estado del ciclo de vida de un caso.

## Artefactos por caso

| Artefacto | Función |
|---|---|
| `metadata.yaml` | Identidad, versión, entradas, salidas y estado del ciclo de vida |
| `validation_spec.yaml` | Fronteras, operandos, umbrales, alcance y evidencia requerida |
| `validation_results.json` | Resultado estructurado generado con `--write-artifacts` |
| `validation_report.md` | Informe técnico canónico y narrativa de ingeniería |
| `provenance.json` | Procedencia y checksums de los artefactos |
| sidecars `*.meta.yaml` | Esquema, unidades y checksum de cada dataset canónico |

`validation_results.json` es un artefacto generado: no se edita manualmente.
El validador tampoco reemplaza la narrativa técnica, las limitaciones ni el
análisis de seguridad de `validation_report.md`.

Esta adaptación conserva `validation_report.md` como informe canónico del
repositorio, en lugar de crear un segundo archivo `VALIDATION.md` con contenido
duplicado. La sección comprendida entre los delimitadores
`PTR-VALIDATION:AUTO` cumple la función de la tabla reproducible solicitada.

## Fuentes de evidencia

La opción `--source` controla la procedencia de los resultados:

- `dataset`: valida únicamente las exportaciones canónicas versionadas;
- `dwsim`: exige resolver una copia temporal del modelo mediante DWSIM
  Automation API y falla si esa ejecución no está disponible;
- `auto`: intenta DWSIM y, si no está disponible, continúa con datasets dejando
  el fallback registrado explícitamente.

La ejecución DWSIM se realiza en un proceso aislado, sobre una copia temporal y
sin guardar el flowsheet. El SHA-256 del archivo versionado debe coincidir antes
y después de la ejecución. La indisponibilidad de DWSIM nunca se presenta como
una ejecución satisfactoria de la API.

## Fronteras y criterios

Las corrientes de entrada, salida e internas se identifican de forma explícita.
Una corriente interna no puede contabilizarse simultáneamente como entrada y
salida de una frontera global. Los intercambiadores con dos fluidos declaran una
frontera de masa independiente por lado.

Los umbrales generales de `0.5 %` para masa y `1.0 %` para energía solo son
valores iniciales para casos nuevos. Prevalecen siempre los límites específicos
de cada caso. Los criterios admitidos por la versión `1.0.0` del manifiesto son:

- balances globales o por lado;
- balance de energía de corrientes;
- isoentalpía;
- rango;
- comparación;
- métrica reportada;
- margen de presión;
- paridad entre las propiedades recalculadas mediante DWSIM API y el dataset
  canónico;
- validadores existentes de metadatos, tablas, unidades y checksums.

Una `reported_metric` identifica una comprobación documentada previamente. No
equivale a una recomputación independiente. Si faltan columnas necesarias, el
criterio se informa como `N_A` o `NOT_RUN`; no se fabrica un `PASS`.

## Estados y alcances

Cada criterio pertenece a uno de cuatro alcances:

- `numerical`: consistencia de balances y resultados numéricos;
- `phenomenon`: controles propios del fenómeno físico o químico;
- `safety`: afirmaciones de seguridad y barreras operacionales;
- `data_quality`: estructura, unidades, completitud y trazabilidad.

Los estados de criterio son `PASS`, `FAIL`, `N_A`, `NOT_RUN` y
`NOT_DEMONSTRATED`. Un margen de seguridad no demostrado no debe convertirse en
`PASS` por el hecho de que los balances termodinámicos sean correctos.

Estos estados son distintos de `draft`, `review`, `validated` y `published`.
Solo una decisión explícita de revisión puede promover el ciclo de vida.

## Ejecución

Desde la raíz del repositorio:

```powershell
python scripts/validate_case.py cases/001_acondicionamiento_agua_lavado_pulpa_kraft --source auto
python scripts/validate_case.py cases/ --source dataset
python scripts/validate_case.py cases/ --source dataset --write-artifacts
python scripts/validate_case.py cases/003_recuperacion_calor_condensado_y_control_contaminacion_cruzada --source dwsim --strict
```

La ejecución ordinaria y el preflight son de solo lectura. La opción
`--write-artifacts` actualiza los resultados estructurados y la sección
delimitada del informe. `--strict` también falla ante criterios obligatorios
`N_A`, `NOT_RUN` o `NOT_DEMONSTRATED`.

El código de salida es `1` ante configuración inválida, error de ejecución,
artefacto obligatorio ausente o un criterio bloqueante en `FAIL`. Sin esas
condiciones, el código es `0`, salvo el endurecimiento solicitado por
`--strict`.

## DWSIM y CI

DWSIM se utiliza localmente en Windows o en un runner manual/autohospedado que
declare la versión requerida. El workflow ordinario de GitHub Actions valida
los datasets y no descarga DWSIM.

La ruta de instalación se resuelve mediante `--dwsim-home`, `DWSIM_HOME`,
`%LOCALAPPDATA%\DWSIM` y las rutas conocidas de `%ProgramFiles%`, en ese orden.
La versión ejecutada debe coincidir con la declarada en el caso.

## Contrato para casos y visualizaciones futuras

Para incorporar un caso nuevo se copia `templates/case_template/`, se completa
`metadata.yaml`, se declaran datasets y fronteras en `validation_spec.yaml` y se
añaden criterios sin modificar el motor.

El futuro dashboard descubrirá directorios `cases/[0-9][0-9][0-9]_*`, cargará
`metadata.yaml` y `validation_results.json`, y encontrará datasets mediante sus
sidecars y figuras bajo `assets/figures/`. Las vistas podrán agruparse por caso,
fenómeno, equipo, estado, versión y fuente de evidencia. Las métricas no deben
extraerse analizando Markdown.
