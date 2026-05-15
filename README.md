# PTR Engineering Cases

> Portafolio técnico de casos reproducibles de ingeniería química industrial.
> Stack open source · FAIR · SI · IUPAC · ISO 8000 · VIM · trazabilidad SHA-256.

[![status](https://img.shields.io/badge/status-foundational--v0.1.0-blue)](./CHANGELOG.md)
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
verificables: cada caso es reproducible end-to-end, validado contra
referencias o balances globales, con metadatos formales, unidades SI y
checksums SHA-256.

## Metodología

`fenómeno → fundamento científico → modelo → simulación/procesamiento →
resultados → validación/QC → trazabilidad → conclusión técnica`

## Stack

- **Principal:** DWSIM · Python (pandas, numpy, scipy) · Power Query · Power BI · Streamlit
- **Complementario (según caso):** OpenChrom, SpectraGryph, OpenMS, ProteoWizard, pyOpenMS, JCAMP-DX, mzML, SQLite, DuckDB, Plotly, Altair, Jupyter

## Gobernanza

- UTF-8 · LF · CSV `,` · decimal `.` · ISO 8601 UTC
- Unidades SI obligatorias; vocabulario controlado en `schemas/`
- Metadatos YAML por caso validados contra JSON Schema
- SemVer · Keep a Changelog · CITATION.cff
- Provenance W3C PROV-lite + SHA-256 por artefacto

Ver `docs/` para detalles normativos.

## Trazabilidad

Cada artefacto declara: `provenance.json` (agentes, actividades, entidades),
`derived_from`, SHA-256, versiones de software y autoría.

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
python scripts/compute_checksums.py --verify cases/<NNN_slug>
```

## Índice de casos

> Vacío en v0.1.0 (arquitectura fundacional). Se autogenerará con
> `scripts/build_case_index.py` cuando el primer caso esté `validated`.

## Roadmap

| Release | Alcance |
|---|---|
| **v0.1.0** | Arquitectura fundacional, plantillas, schemas, scripts, CI |
| **v0.2.0** | Refinamiento de plantillas y vocabularios controlados |
| **v0.3.0** | Automatización CI/CD endurecida + tests con cobertura ≥ 80% |
| **v1.0.0** | Primer caso reproducible publicado |

## Licencia

- **Código:** MIT (ver `LICENSE`)
- **Documentación:** CC BY 4.0 (ver `LICENSE-docs`)
- **Datos sintéticos:** CC0 1.0 (declarado por dataset)

## Citación

Ver `CITATION.cff`.

## Contacto

Roberto Flores — `roberto.flores.n1987@gmail.com`
