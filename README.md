# PTR Engineering Cases

> Portafolio técnico de casos reproducibles de ingeniería química industrial.
> Stack open source · FAIR · SI · IUPAC · ISO 8000 · VIM · trazabilidad SHA-256.

[![status](https://img.shields.io/badge/status-case--portfolio--v0.2.0-blue)](./CHANGELOG.md)
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
python scripts/validate_metadata.py cases/<NNN_slug>
python scripts/unit_consistency_check.py cases/<NNN_slug>
python scripts/compute_checksums.py --verify cases/<NNN_slug>
pytest tests/ -q
```

La simulación debe abrirse desde la copia clonada y resolverse con la versión de
software declarada por el caso. Los pasos adicionales se documentan en el README
de cada caso.

## Índice de casos

| ID | Caso | Dominio | Equipos principales | Software | Estado |
|---|---|---|---|---|---|
| [001](./cases/001_acondicionamiento_agua_lavado_pulpa_kraft/) | Acondicionamiento de agua para lavado de pulpa Kraft | Bombeo y calentamiento de agua | Bomba centrífuga, calentador | DWSIM 9.0.5, Python 3.13.5 | `review` |

### Caso fundacional 001

El primer caso implementado establece el patrón canónico del portafolio. Modela
una línea auxiliar simplificada de agua asociada conceptualmente al lavado de
pulpa Kraft, con datos sintéticos y sin información operacional interna de CMPC.
Incluye:

- archivo de simulación DWSIM versionado;
- balances globales de masa y energía;
- comprobaciones hidráulica y calorimétrica independientes;
- dataset de resultados y sidecar de metadatos;
- supuestos, limitaciones, informe de validación y checklist QC;
- procedencia y checksums SHA-256.

El modelo numérico obtuvo veredicto `PASS`. El caso permanece en `review` hasta
confirmar su reapertura y resolución desde un clon independiente del repositorio.

## Roadmap

| Release | Alcance |
|---|---|
| **v0.1.0** | Arquitectura fundacional: plantillas, schemas, scripts, CI y gobernanza |
| **v0.2.0** | Primer caso integrado, índice de casos y sincronización documental |
| **v0.3.0** | Nuevos casos contextuales y endurecimiento de validadores de datasets, unidades y checksums |
| **v0.4.0** | Visualizaciones técnicas, automatización del índice y cobertura de tests ≥ 80 % |
| **v1.0.0** | Portafolio inicial validado y publicado con varios casos reproducibles |

Próximas líneas de desarrollo previstas:

1. recuperación de calor y precalentamiento de corrientes;
2. flash de condensado y recuperación de vapor secundario;
3. recirculación de agua con purga y make-up;
4. operaciones unitarias Kraft de complejidad progresiva.

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
