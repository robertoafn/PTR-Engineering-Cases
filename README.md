# PTR Engineering Cases

> Portafolio técnico de casos reproducibles de ingeniería química industrial.
> Stack open source · FAIR · SI · IUPAC · ISO 8000 · VIM · trazabilidad SHA-256.

[![release](https://img.shields.io/badge/release-v0.5.0-blue)](./CHANGELOG.md)
[![license-code](https://img.shields.io/badge/code-MIT-green)](./LICENSE)
[![license-docs](https://img.shields.io/badge/docs-CC--BY--4.0-lightgrey)](./LICENSE-docs)

---

## ¿Quién soy?

Ingeniero en Química Industrial enfocado en simulación de procesos, QA/QC,
metrología, validación de datos, ETL científico y documentación reproducible.
Construyo casos auditables que conectan **fenómeno → modelo → simulación →
validación → trazabilidad → conclusión**.

## ¿Qué resuelve este repositorio?

Demuestra, caso por caso, competencia técnica integral mediante artefactos
verificables. Cada caso busca ser reproducible end-to-end, validado contra
referencias, balances globales o cálculos independientes, con metadatos formales,
unidades SI y checksums SHA-256.

El repositorio combina ingeniería de procesos, control de calidad de datos y
prácticas de ingeniería de software. Los casos pueden usar datos sintéticos,
hipotéticos, abiertos o experimentales, siempre declarados explícitamente.

## Metodología

`fenómeno → fundamento científico → modelo → simulación/procesamiento →
resultados → validación/QC → trazabilidad → conclusión técnica`

## Stack

- **Principal:** DWSIM · Python (pandas, numpy, scipy) · Power Query · Power BI · Streamlit
- **Complementario, según caso:** OpenChrom, SpectraGryph, OpenMS, ProteoWizard,
  pyOpenMS, JCAMP-DX, mzML, SQLite, DuckDB, Plotly, Altair y Jupyter

## Gobernanza

- UTF-8 · LF · CSV `,` · decimal `.` · ISO 8601 UTC
- Unidades SI obligatorias y vocabulario controlado en `schemas/`
- Metadatos YAML por caso validados contra JSON Schema
- SemVer · Keep a Changelog · CITATION.cff
- Provenance W3C PROV-lite + SHA-256 por artefacto
- Estados del ciclo de vida: `draft → review → validated → published`

Ver [`docs/`](./docs/) para la metodología, gobernanza, convenciones y modelo de
trazabilidad.

## Trazabilidad

Cada caso declara `provenance.json` con agentes, actividades, entidades,
relaciones `derived_from`, versiones de software y checksums SHA-256 de los
artefactos principales.

## Reproducir un caso

```bash
git clone https://github.com/robertoafn/PTR-Engineering-Cases.git
cd PTR-Engineering-Cases
python -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
python scripts/preflight.py cases/<NNN_slug>

# Controles individuales equivalentes
python scripts/validate_metadata.py cases/<NNN_slug>
python scripts/validate_tables.py cases/<NNN_slug>
python scripts/unit_consistency_check.py cases/<NNN_slug>
python scripts/compute_checksums.py --verify cases/<NNN_slug>
python scripts/validate_case.py cases/<NNN_slug> --source dataset
pytest tests/ -q
```

La simulación debe abrirse desde la copia clonada y resolverse con la versión de
software declarada por el caso. Los pasos adicionales se documentan en el README
de cada caso.

## Dashboard explicativo

La línea v0.5.0 incorpora una aplicación Streamlit de sólo lectura que descubre
los casos implementados y prioriza la comprensión de sus fenómenos. Cada caso
se recorre como `pregunta → flowsheet → mecanismo → ecuación → datos →
interpretación → límites`, con figuras específicas como apoyo a la explicación:

```bash
streamlit run dashboards/streamlit/app.py
```

La interfaz consume los CSV, metadatos, figuras y `validation_results.json`
versionados; no modifica ni recalcula las simulaciones. Los criterios y estados
se mantienen en la vista secundaria `Rigor y fuentes`: respaldan la
trazabilidad, pero no sustituyen la interpretación científica. Ver
[`dashboards/streamlit/README.md`](./dashboards/streamlit/README.md) y el
[`protocolo del dashboard`](./docs/10_dashboard_streamlit.md).

## Índice de casos

| ID | Caso | Dominio | Equipos principales | Software | Estado | Validación automática |
|---|---|---|---|---|---|---|
| [001](./cases/001_acondicionamiento_agua_lavado_pulpa_kraft/) | Acondicionamiento de agua para lavado de pulpa Kraft | Bombeo y calentamiento de agua | Bomba centrífuga, calentador | DWSIM 9.0.5, Python 3.13.5 | `validated` | [`PASS`](./cases/001_acondicionamiento_agua_lavado_pulpa_kraft/validation_report.md) |
| [002](./cases/002_recuperacion_vapor_flash_y_particion_de_volatiles/) | Recuperación de vapor flash y partición de compuestos volátiles | Flash isoentálpico y equilibrio vapor-líquido | Válvula, separador gas-líquido | DWSIM 9.0.5, OpenChrom 1.6.14, Python 3.13.5 | `review` | [`FAIL` (paridad API↔dataset)](./cases/002_recuperacion_vapor_flash_y_particion_de_volatiles/validation_report.md) |
| [003](./cases/003_recuperacion_calor_condensado_y_control_contaminacion_cruzada/) | Recuperación de calor de condensado y control de contaminación cruzada | Transferencia de calor y control hidráulico de contaminación | Intercambiador de carcasa y tubos (HX-301) | DWSIM 9.0.5, Python 3.13.5 | `review` | [`CONDITIONAL`](./cases/003_recuperacion_calor_condensado_y_control_contaminacion_cruzada/validation_report.md) |

La validación automática y el estado del ciclo de vida son dimensiones
independientes. El protocolo, los estados de criterio y el uso de DWSIM se
describen en [`docs/09_validation_protocol.md`](./docs/09_validation_protocol.md).

### Ubicación conceptual en el proceso productivo Kraft

Los casos representan operaciones unitarias y servicios auxiliares de una
cadena didáctica; no constituyen una simulación integrada de una planta
completa.

| Caso | Área o etapa representada | Función productiva | Relación entre casos |
|---|---|---|---|
| 001 | Servicio auxiliar previo al lavado de pulpa | Bombear y calentar agua que podría alimentar una operación de desplazamiento de licor negro | Caso independiente; no intercambia corrientes con 002–003 |
| 002 | Gestión de condensados calientes asociada a evaporación y recuperación | Reducir presión, generar vapor flash y separar una fase líquida con trazas de metanol | Produce conceptualmente el condensado líquido utilizado por el Caso 003 |
| 003 | Recuperación indirecta de calor desde condensado residual | Precalentar agua limpia mediante HX-301 y evaluar la dirección hidráulica de una fuga hipotética | Usa el caudal, la temperatura, la presión y la fracción másica de metanol de `MSTR-204` como base redondeada para `MSTR-301`; las propiedades restantes se recalculan en el Caso 003 |

### Caso fundacional 001

El primer caso implementado establece el patrón canónico del portafolio. Modela
una línea auxiliar simplificada de agua asociada conceptualmente al lavado de
pulpa Kraft, con datos sintéticos y sin información operacional de una
instalación real.
Incluye:

- archivo de simulación DWSIM versionado;
- balances globales de masa y energía;
- comprobaciones hidráulica y calorimétrica independientes;
- dataset de resultados y sidecar de metadatos;
- supuestos, limitaciones, informe de validación y checklist QC;
- procedencia y checksums SHA-256.

El modelo numérico, los controles automatizados y la validación de ejecución
realizada por el autor obtuvieron veredicto `PASS`. El archivo versionado fue
abierto, resuelto e inspeccionado en DWSIM 9.0.5, por lo que el Caso 001 se
encuentra en estado `validated`.

### Caso 002 — Recuperación de vapor flash y partición de volátiles

El segundo caso modela un condensado sintético de agua y metanol que se expande
de forma isoentálpica y se separa en vapor flash y líquido residual. Integra la
simulación DWSIM con cromatogramas GC-FID sintéticos procesados en OpenChrom,
datos estructurados, controles de balance y trazabilidad por checksum.

El escenario base obtuvo un rendimiento másico de vapor flash de `0.10488775`
y una recuperación de metanol hacia el vapor de `0.42793470`. La revalidación
mediante DWSIM mantiene conformes los balances, pero detecta una desviación de
`0.115554596249 %` entre la energía de `MSTR-204` recalculada por la API y la
publicada en el CSV, sobre el umbral de paridad de `0.05 %`. El caso se mantiene
en estado `review` y no debe promoverse hasta reconciliar esa evidencia; tampoco
representa una validación experimental o industrial. Ver
[Caso 002](./cases/002_recuperacion_vapor_flash_y_particion_de_volatiles/).

### Caso 003 — Recuperación de calor de condensado y control de contaminación cruzada

El tercer caso continúa la cadena de proceso desde el condensado líquido
caliente del Caso 002. Modela el intercambiador de carcasa y tubos HX-301 para
precalentar agua limpia de proceso y evalúa el diferencial de presión como
barrera operativa frente a una eventual fuga de condensado con trazas de
metanol.

El escenario simulado entrega una carga térmica de `1.063410 MW`: el agua
limpia se precalienta de `293.150 K` a `333.150 K` y el condensado se enfría de
`406.649 K` a `384.187 K`. El diferencial calculado entre el lado limpio y el
contaminado es `0 Pa`; este valor es un límite sin margen y no demuestra control
operacional de contaminación cruzada. Una aplicación real requiere presión
mayor en el lado limpio durante todo el dominio operativo, monitoreo del
diferencial y medidas adicionales de detección, aislamiento o diseño mecánico
según el análisis de riesgos. El caso permanece en `review`; sus entradas y
resultados son sintéticos o simulados y no representan condiciones
operacionales reales. Ver [Caso 003](./cases/003_recuperacion_calor_condensado_y_control_contaminacion_cruzada/).

## Roadmap

| Release | Alcance |
|---|---|
| **v0.1.0** | Arquitectura fundacional: plantillas, schemas, scripts, CI y gobernanza |
| **v0.2.0** | Primer caso integrado, índice de casos y sincronización documental |
| **v0.3.0** | Incorporación del Caso 003, revisión de casos contextuales y endurecimiento de validadores de datasets, unidades y checksums |
| **v0.4.0** | Motor declarativo de validación, integración opcional con DWSIM API y resultados estructurados por caso |
| **v0.5.0 (release actual)** | Dashboard científico Streamlit, visualizaciones explicativas, índice automático y propuesta metrológica del Caso 004 |
| **v1.0.0** | Portafolio inicial validado y publicado con varios casos reproducibles |

El plan verificable de la versión se mantiene en
[`docs/ROADMAP_v0.5.0.md`](./docs/ROADMAP_v0.5.0.md).

Próximas líneas de desarrollo previstas:

1. promover la [propuesta del Caso 004](./docs/proposals/004_incertidumbre_gum_monte_carlo_hx301.md)
   cuando exista un presupuesto trazable de incertidumbre para HX-301;
2. recirculación de agua con purga y make-up;
3. operaciones unitarias Kraft de complejidad progresiva.

## Uso profesional

El repositorio está diseñado como evidencia verificable de competencias en:

- balances de materia y energía;
- simulación y selección de modelos termodinámicos;
- validación independiente de resultados;
- QA/QC, metrología y criterios de aceptación;
- ingeniería de datos científicos;
- trazabilidad, versionado, pruebas y CI/CD.

## Licencia

- **Código:** MIT, ver [`LICENSE`](./LICENSE)
- **Documentación:** CC BY 4.0, ver [`LICENSE-docs`](./LICENSE-docs)
- **Datos sintéticos:** CC0 1.0, declarado por dataset

## Citación

Ver [`CITATION.cff`](./CITATION.cff).

## Contacto

Roberto Flores — `roberto.flores.n1987@gmail.com`
