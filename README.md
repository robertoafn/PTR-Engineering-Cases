# PTR Engineering Cases

> Portafolio técnico de casos reproducibles de ingeniería química industrial.  
> DWSIM · Python · FAIR · SI · QA/QC · metrología · trazabilidad SHA-256.

[![validate](https://github.com/robertoafn/PTR-Engineering-Cases/actions/workflows/validate.yml/badge.svg)](https://github.com/robertoafn/PTR-Engineering-Cases/actions/workflows/validate.yml)
[![lint](https://github.com/robertoafn/PTR-Engineering-Cases/actions/workflows/lint.yml/badge.svg)](https://github.com/robertoafn/PTR-Engineering-Cases/actions/workflows/lint.yml)
[![license-code](https://img.shields.io/badge/code-MIT-green)](./LICENSE)
[![license-docs](https://img.shields.io/badge/docs-CC--BY--4.0-lightgrey)](./LICENSE-docs)

## Propósito profesional

PTR Engineering Cases convierte ejercicios y simulaciones en evidencia técnica
auditable. Cada caso conecta:

```text
fenómeno → fundamento → modelo → simulación → datos → validación → trazabilidad → conclusión
```

El repositorio demuestra la capacidad de formular una pregunta de ingeniería,
construir un modelo, verificar sus resultados, identificar limitaciones y
publicar artefactos reproducibles. No pretende representar condiciones internas
de una empresa ni sustituir datos operacionales reales.

## Perfil del autor

Roberto Flores, Ingeniero en Química Industrial, enfocado en:

- simulación y análisis de procesos;
- balances de materia y energía;
- QA/QC, metrología y criterios de aceptación;
- validación de datos y ETL científico;
- documentación reproducible y control de versiones.

## Estado actual

El repositorio contiene una arquitectura funcional y un primer caso fundacional
validado por el autor. La gobernanza ya está operativa; la cobertura industrial
crecerá mediante casos progresivos de mayor extensión, número de equipos y
complejidad de proceso.

### Evidencia publicada

| Evidencia | Estado |
|---|---|
| Simulación DWSIM versionada | Disponible |
| Dataset CSV con sidecar YAML | Disponible |
| Balances y cálculos independientes | PASS |
| Metadatos validados con JSON Schema | PASS |
| Consistencia de unidades SI | PASS |
| Checksums SHA-256 | PASS |
| Pruebas automatizadas y linting | Integrados en CI |
| Reproducción independiente externa | Pendiente |

La validación actual del Caso 001 corresponde a reapertura, resolución e
inspección ejecutadas por el autor. No se presenta como revisión externa ni como
validación contra datos de planta.

## Metodología y gobernanza

Cada caso utiliza un contrato documental común:

- UTF-8, LF, CSV con separador `,`, decimal `.` e ISO 8601 UTC;
- unidades SI y vocabularios controlados;
- `metadata.yaml` validado contra JSON Schema;
- datasets con sidecar `.meta.yaml`;
- separación entre columna física del CSV (`column`) y símbolo científico
  (`symbol`);
- procedencia W3C PROV-lite y relaciones `derived_from`;
- checksums SHA-256 de artefactos principales;
- SemVer, Keep a Changelog y `CITATION.cff`;
- ciclo de vida `draft → review → validated → published`.

Ver [`docs/`](./docs/), [`CONTRIBUTING.md`](./CONTRIBUTING.md) y
[`AGENTS.md`](./AGENTS.md).

## Stack demostrado

Las herramientas siguientes ya participan en artefactos o controles publicados:

- DWSIM 9.0.5;
- Python 3.11+;
- pandas, PyYAML y jsonschema;
- pytest y Ruff;
- GitHub Actions;
- CSV, YAML, JSON, BibTeX y Markdown.

Herramientas como Power BI, Streamlit, DuckDB, Jupyter, OpenChrom, OpenMS,
Plotly o Altair se incorporarán al stack demostrado únicamente cuando exista un
caso reproducible que las utilice.

## Reproducción y preflight

### Instalación

```bash
git clone https://github.com/robertoafn/PTR-Engineering-Cases.git
cd PTR-Engineering-Cases
python -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Control completo de un caso

```bash
python scripts/preflight.py cases/001_acondicionamiento_agua_lavado_pulpa_kraft
```

### Control completo del portafolio

```bash
python scripts/preflight.py cases/
```

El preflight ejecuta nomenclatura, metadatos, datasets, unidades, checksums,
pruebas y linting. Los validadores fallan ante objetivos inexistentes o vacíos;
no aceptan un `PASS` sin artefactos descubiertos.

## Flujo para nuevos casos desde ChatGPT Desktop

1. Sincronizar `main` y revisar el estado local.
2. Crear una rama `case/NNN_slug`.
3. Copiar [`templates/case_template/`](./templates/case_template/).
4. Definir un objetivo verificable y la frontera del sistema.
5. Construir la simulación, cálculos y datasets.
6. Documentar supuestos, limitaciones, referencias y criterios de aceptación.
7. Actualizar procedencia y checksums:

   ```bash
   python scripts/compute_checksums.py cases/NNN_slug
   ```

8. Ejecutar:

   ```bash
   python scripts/preflight.py cases/NNN_slug
   ```

9. Actualizar el índice y los changelogs.
10. Publicar mediante Pull Request; nunca modificar `main` directamente.

Las reglas persistentes para agentes están en [`AGENTS.md`](./AGENTS.md). Los
casos pueden ser breves o extensos, pero todos deben conservar el mismo contrato
de trazabilidad y validación.

## Índice de casos

| ID | Caso | Dominio | Equipos principales | Software | Estado |
|---|---|---|---|---|---|
| [001](./cases/001_acondicionamiento_agua_lavado_pulpa_kraft/) | Acondicionamiento de agua para lavado de pulpa Kraft | Bombeo y calentamiento de agua | Bomba centrífuga, calentador | DWSIM 9.0.5, Python 3.13.5 | `validated` |

### Caso fundacional 001

Modela una línea auxiliar simplificada de agua asociada conceptualmente al
lavado de pulpa Kraft. Emplea datos sintéticos y no contiene información
operacional interna de CMPC.

Incluye:

- archivo `.dwxmz` versionado;
- balances globales de masa y energía;
- comprobaciones hidráulica y calorimétrica independientes;
- dataset de resultados con metadatos y clave primaria;
- supuestos, limitaciones, validación y checklist QA/QC;
- procedencia y checksums SHA-256.

Resultados principales para las condiciones simuladas:

- caudal de agua: `10 kg/s`;
- potencia de bomba: `4.01711 kW`;
- carga térmica: `1670.50072 kW`;
- residuo global de masa: `0 kg/s`;
- error relativo del balance energético: `2.69E-07 %`.

## Roadmap técnico

| Release | Alcance |
|---|---|
| **v0.2.x** | Endurecimiento de validadores, preflight local y reglas para agentes |
| **v0.3.0** | Nuevos casos básicos y progresivos; validación de datasets ampliada |
| **v0.4.0** | Figuras ejecutivas, automatización del índice y cobertura de tests ≥ 80 % |
| **v0.5.0** | Casos con reciclajes, flash, integración energética y análisis de sensibilidad |
| **v1.0.0** | Portafolio inicial con varios casos reproducibles y publicación estable |

Líneas previstas:

1. intercambiadores y recuperación de calor;
2. válvulas y flash de condensado;
3. recirculación de agua con purga y make-up;
4. mezclas y selección de paquetes termodinámicos;
5. evaporación y operaciones Kraft de complejidad progresiva;
6. reactores, separaciones y tratamiento de efluentes.

## Política de datos y uso

- Los datos deben clasificarse como `synthetic`, `hypothetical`, `simulated` o
  `literature`.
- No se aceptan datos operacionales internos, confidenciales o sin licencia.
- Los resultados no deben utilizarse para diseño de planta o decisiones
  operacionales fuera del dominio declarado por cada caso.
- Hechos, supuestos, estimaciones y resultados simulados deben diferenciarse.

## Uso profesional

El repositorio sirve como evidencia verificable de competencias en:

- formulación de problemas de ingeniería;
- balances de materia y energía;
- simulación y selección de modelos;
- validación independiente de resultados numéricos;
- QA/QC, metrología y criterios de aceptación;
- ingeniería de datos científicos;
- trazabilidad, versionado, pruebas y CI/CD.

## Licencias

- Código: MIT, ver [`LICENSE`](./LICENSE).
- Documentación: CC BY 4.0, ver [`LICENSE-docs`](./LICENSE-docs).
- Datos sintéticos: CC0 1.0, declarado por dataset.

## Citación y contacto

Ver [`CITATION.cff`](./CITATION.cff).

Roberto Flores — `roberto.flores.n1987@gmail.com`
