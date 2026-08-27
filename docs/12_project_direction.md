# 12 — Estado y dirección del proyecto

## Visión

**Periodic Table Research — From Elements to Industrial Decisions** evoluciona
desde un portafolio de simulaciones reproducibles hacia un ecosistema
interoperable de casos científicos e industriales de ingeniería química.

La arquitectura conserva FAIR, unidades SI, nomenclatura IUPAC, QC,
procedencia, versionado y reproducibilidad, y extiende la cadena de valor:

> elementos → sustancias → propiedades → fenómenos → modelos → simulación →
> evidencia experimental → proceso → energía → ambiente → economía →
> supply chain → decisión industrial

El objetivo no es acumular casos. Cada caso nuevo debe producir entidades,
datos, modelos, evidencia o decisiones que puedan ser verificados y
reutilizados por los siguientes.

## Estado comprobable

| Capa | Estado | Evidencia actual |
|---|---|---|
| Gobernanza FAIR, SI, QC, provenance y SemVer | Implementada | `docs/`, `schemas/`, validadores, tests y CI |
| Casos PTR 001–004 | Baseline publicado | Estados `PASS`, `FAIL` y `CONDITIONAL` conservados sin homogeneizarlos |
| Línea de Literature Cases | Implementada | Caso 102 promovido con fuente inmutable, licencia, hashes y procedencia |
| Contrato de ejecuciones DWSIM | Implementado | `SimulationRun` v1.0.0, ADR 0001, fixture y pruebas |
| Réplicas DWSIM 10.2.0 del Caso 102 | Contexto local en revisión | Cuatro estados guardados del autor; no promovidos ni tratados como validación independiente |
| VLE experimental de Álvarez et al. | Borrador local | Transcripción preliminar no versionada; requiere revisión y decisión de derechos antes de promoverse |
| Ingesta canónica DWSIM/literatura | Planificada | Debe construirse sobre `SimulationRun`, sidecars, IDs y provenance existentes |
| Modelo estrella y Power BI | Planificado | Consumirá datasets gobernados; no leerá directamente archivos DWSIM |
| JSON-LD y Knowledge Graph transversal | Planificado | Reutilizará IDs y relaciones validadas; no será una segunda fuente de verdad |
| PTR Industrial Decision Core | Dirección progresiva | Balances y deberes energéticos ya existen en casos; desempeño energético comparativo, CAPEX, GHG, economía, logística y supply chain entrarán después de la validación científico-técnica |

Esta tabla es una frontera de afirmaciones: una capacidad planificada no debe
describirse como implementada hasta que tenga artefactos versionados, contrato,
procedencia y controles reproducibles.

## Función de las herramientas

- **DWSIM** es el laboratorio computacional principal para flowsheets y
  propiedades; cada inspección o ejecución promovida se registra como
  `SimulationRun`.
- **Python** implementa extracción, transformaciones deterministas, QC,
  validación y generación de datasets canónicos.
- **SQL, SQLite o DuckDB** podrán materializar consultas y modelos analíticos
  reproducibles; no sustituyen los archivos canónicos ni sus sidecars.
- **APIs** automatizan interfaces declaradas y versionadas. Una respuesta de
  API debe conservar parámetros, versión y artefactos suficientes para ser
  auditada.
- **Streamlit** es la visualización científica implementada actualmente.
- **Power BI** es la proyección analítica planificada mediante un modelo
  dimensional gobernado.
- **Obsidian** puede organizar investigación local. **JSON-LD y Knowledge
  Graph** serán capas de interoperabilidad construidas desde IDs canónicos, no
  desde texto libre ni nombres de archivo.

## Caso piloto 102

**Case 102 — Methanol–Water Distillation** prueba la arquitectura de extremo a
extremo. Su objetivo es comparar Raoult, NRTL, UNIQUAC y Modified UNIFAC
(Dortmund), contrastar predicciones con VLE experimental y, sólo después,
extender el caso hacia energía, CAPEX, GHG y decisión industrial.

| Gate | Entregable | Estado |
|---|---|---|
| G0 | Fuente FOSSEE inmutable, licencia, identidad y hashes | Completado |
| G1 | Contrato `SimulationRun` y política de versiones DWSIM | Completado |
| G2 | Inventario y procedencia de las cuatro réplicas del autor | Local; no promovido |
| G3 | Dataset VLE experimental revisado, licenciable y canónico | Pendiente |
| G4 | Recálculos limpios en DWSIM estable con configuración controlada | Pendiente |
| G5 | Benchmark `T-x-y` a presión común con métricas y residuos | Pendiente |
| G6 | Comparación de columna, balances, perfiles y deberes | Pendiente |
| G7 | Extensión energía → CAPEX/GHG → decisión | Pendiente |

El benchmark VLE precede a la comparación integral de columna. Los parámetros
termodinámicos, el modelo de entalpía y la versión DWSIM son factores
experimentales explícitos; no se atribuirán todas las diferencias al nombre del
paquete termodinámico.

## Secuencia de desarrollo

1. Consolidar la arquitectura y la documentación del repositorio.
2. Publicar el Caso 102 como primer caso científico-industrial completo.
3. Normalizar la ingesta de simulaciones DWSIM y literatura experimental.
4. Construir datasets canónicos, QC automático y provenance reproducible.
5. Implementar el modelo estrella y el dashboard interoperable de Power BI.
6. Incorporar progresivamente PTR Industrial Decision Core y el Knowledge
   Graph transversal.
7. Migrar capacidades reutilizables de logística, supply chain y análisis
   comercial al mismo modelo semántico.

La secuencia expresa dependencias, no siete proyectos paralelos. Una capa se
promueve cuando su entrada es gobernada y su salida puede ser validada sin
depender del estado local de una herramienta.

## Criterios para aceptar complejidad

Una entidad, schema, pipeline, base de datos, API o visualización nueva debe
demostrar al menos una de estas mejoras:

- mayor reproducibilidad o automatización determinista;
- interoperabilidad entre dos o más consumidores reales;
- validación o QC que antes no podía ejecutarse;
- trazabilidad más completa entre evidencia y conclusión;
- mejor capacidad para comparar alternativas o decidir.

Si el beneficio no puede probarse, se reutiliza la estructura existente o se
mantiene la idea como propuesta documental.
