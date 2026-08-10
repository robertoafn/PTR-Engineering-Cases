# Changelog

Todos los cambios notables a este repositorio quedan registrados aquí.

El formato sigue [Keep a Changelog 1.1](https://keepachangelog.com/en/1.1.0/)
y este proyecto adhiere a [Semantic Versioning 2.0.0](https://semver.org/).

## [Unreleased]

## [0.6.0] - 2026-08-09

### Added
- Caso 004 para HX-301 con especificación `U = 1000 W/(m²·K)`, `A = 13 m²`,
  margen nominal limpio−contaminado de `+50 kPa` y criterios separados para
  cierre UA, fase, calorimetría, sensibilidad y validación cruzada.
- Explicación científica del Caso 004 en Streamlit, con perfil contracorriente,
  reconstrucciones de carga, barrido U–caudal, comparación de presiones y
  estados vacíos explícitos para evidencia externa pendiente.
- Roadmap v0.6.0 para integrar el nuevo caso sin modificar el cierre histórico
  del release v0.5.0.
- Paridad real del Caso 002 reejecutada mediante DWSIM API: estados dentro de
  tolerancia y `FAIL` energético de `0.115554596 %` en `MSTR-204`.
- Línea `Literature_cases/` iniciada con el Caso FOSSEE 102, sus dos archivos
  originales inmutables, manifiesto, procedencia, licencia, checksums e informe
  de ingreso.
- Validador genérico de Literature Cases para tamaños, SHA-256, rutas seguras y
  comparación byte a byte opcional contra el corpus local.

### Changed
- La propuesta GUM/Monte Carlo sobre HX-301 se renumera como Caso 005 y adopta
  el Caso 004 como futuro punto nominal, sin generar resultados de incertidumbre.
- El índice, overview, protocolo del dashboard y catálogo editorial extienden
  la continuidad conceptual a `002 → 003 → 004 → 005 propuesto`.
- El dashboard distingue el cierre de una parametrización UA de una validación
  independiente de U, A, propiedades termodinámicas o seguridad.
- Los generadores y crosschecks del Caso 004 validan colisiones de rutas; las
  figuras leen estados, parámetros y margen hidráulico desde datasets
  versionados en vez de duplicar valores manuales.
- El alcance de desarrollo de los Casos PTR 001-004 se cierra conservando sus
  estados reales; el trabajo nuevo se orienta primero a casos FOSSEE existentes.
- El corpus `references/Literature_cases_references/` queda excluido de Git;
  sólo se publican casos seleccionados bajo `Literature_cases/`.
- La figura de destilación metanol-agua se reasigna del Caso 003 al Caso 102.

### Validation
- El Caso 004 conserva ciclo de vida `review` y veredicto `CONDITIONAL` mientras
  existan advertencia de fase, crosschecks externos `NOT_RUN` y la paridad
  energética adversa del Caso 002; `+50 kPa` se interpreta sólo como orden
  nominal de presiones.
- Caso 102: `SOURCE_BASELINE_VERIFIED`; 2/2 archivos coinciden en tamaño,
  SHA-256 y contenido con el corpus local. La paridad DWSIM 9.0.5 y el contraste
  termodinámico permanecen `NOT_RUN`.
- Se registra, sin ocultarla, la discrepancia entre DWSIM v6.5 Classic UI de la
  ficha FOSSEE y el build 5.5.6886.34470 embebido.

## [0.5.0] - 2026-08-01

### Added
- Dashboard Streamlit auto-descubrible con mapa científico, estudio por caso,
  conexiones entre fenómenos y una vista separada de rigor y fuentes.
- Transformaciones didácticas reproducibles para explicar potencia hidráulica,
  calor sensible, flash isoentálpico, partición de metanol, cromatografía,
  intercambio térmico, LMTD y margen hidráulico desde los datasets publicados.
- Catálogo editorial estructurado que relaciona fenómenos y ecuaciones con los
  IDs de criterios publicados sin duplicar la evidencia cuantitativa.
- Protocolo de extensión y pruebas automatizadas de carga, cobertura del
  catálogo, estados y separación entre calidad de datos y fenómeno físico.
- Propuesta del Caso 004 para propagar incertidumbre GUM/Monte Carlo sobre
  HX-301, con mensurandos, covarianzas, convergencia y criterios de promoción.

### Changed
- El roadmap v0.5.0 queda detallado con entregables, QA y definición de cierre.
- La documentación principal incorpora la ejecución local del dashboard y la
  continuidad conceptual `002 → 003 → 004`.
- La jerarquía del dashboard cambia de validación primero a `pregunta → figura
  → mecanismo → ecuación → datos → interpretación → límites`; los estados de
  control quedan como respaldo auditable y no como conclusión científica.
- Todas las vistas mantienen texto oscuro sobre fondos claros y las figuras
  incorporan lectura guiada, unidades y límites de interpretación.

### Validation
- Pruebas específicas del dashboard: 11 `PASS`, incluidos cálculos científicos,
  catálogo narrativo, recorrido de las cuatro vistas, advertencias de los casos
  002 y 003 y el control que impide volver a declarar texto blanco.
- Preflight integral: 55 pruebas, Ruff, naming, 3 metadatos, 4 tablas, unidades
  en 7 archivos y checksums en `PASS`.
- Arranque Streamlit y endpoint local de salud HTTP: `200 OK`.

## [0.4.0] - 2026-07-25

### Added
- Motor declarativo `scripts/validate_case.py`, esquemas JSON y pruebas para
  validar balances, fenómenos, unidades, checksums y paridad API-dataset.
- Especificaciones y resultados estructurados de validación para los casos
  001, 002 y 003, preparados para el futuro dashboard.
- Adaptador local de DWSIM Automation API para Windows y protocolo reproducible
  en `docs/09_validation_protocol.md`.

### Changed
- El README distingue el estado del ciclo de vida del resultado automático.
- El preflight y GitHub Actions ejecutan la matriz cuantitativa en modo
  dataset; la plantilla de casos declara el nuevo contrato de validación.
- Versiones de los casos 001, 002 y 003 sincronizadas como `0.1.3`, `0.1.2`
  y `0.1.2`, respectivamente.

### Validation
- Caso 001: `PASS` con DWSIM Automation API.
- Caso 002: `FAIL` de reproducibilidad por una desviación de
  `0.115554596249 %` entre API y CSV para `MSTR-204_LIQUIDO_FLASH`; sus
  balances y controles de fenómeno permanecen en `PASS`.
- Caso 003: `CONDITIONAL`; la validación térmica pasa y el margen hidráulico
  continúa `NOT_DEMONSTRATED`.
- Suite completa: 44 pruebas y Ruff en `PASS`; naming, 3 metadatos, 4 tablas,
  unidades en 7 archivos y checksums verificados.
- No se modificaron simulaciones ni datasets para forzar estos resultados.

## [0.3.0] - 2026-07-25

### Added
- Caso `003_recuperacion_calor_condensado_y_control_contaminacion_cruzada`, en
  estado `review`, con simulación DWSIM del intercambiador HX-301, resultados
  de proceso, figura de flowsheet, metadatos, procedencia, supuestos,
  checklist QC, informe de validación y referencias.

### Changed
- Actualizados el índice de casos, el resumen técnico y el roadmap del README
  para incorporar el Caso 003 como continuación del condensado residual del
  Caso 002.
- Actualizado `docs/00_overview.md` para reflejar los tres casos integrados y
  el criterio de control hidráulico de contaminación cruzada del Caso 003.
- Separada la validación térmica del Caso 003 de la evaluación de seguridad:
  `P_limpio - P_contaminado = 0 Pa` se documenta como condición sin margen,
  no como demostración de control operacional.
- Los sidecars de datasets ahora enlazan cada símbolo científico con su columna
  CSV mediante el campo `column`, documentan todas las columnas canónicas y
  declaran su clave primaria.
- Añadidos `scripts/preflight.py` y `requirements-ci.txt` para un control local
  único y un entorno mínimo de gobernanza en GitHub Actions.
- Eliminadas las referencias corporativas y documentada la ubicación
  conceptual de cada caso dentro de una cadena productiva Kraft genérica.
- Sincronizadas las versiones de los casos 001, 002 y 003 como `0.1.2`,
  `0.1.1` y `0.1.1`, respectivamente, junto con sus datasets modificados.

### Fixed
- `compute_checksums.py` ahora verifica correctamente una ruta de caso
  individual y falla ante rutas sin `provenance.json`.
- `unit_consistency_check.py` valida los campos `unit` reales de entradas y
  salidas de `metadata.yaml`.
- CI valida los datasets canónicos bajo `cases/`; una ejecución con cero
  datasets deja de producir un falso positivo.
- Sincronizado el checksum obsoleto del sidecar de resultados del Caso 001 con
  el CSV y su `provenance.json`.
- Corregido el flujo de energía derivado de `MSTR-303` en el dataset del Caso
  003 para que sea consistente con caudal y entalpía específica publicados.

### Validation
- Preflight integral aprobado para los tres casos.
- 3 metadatos y 4 datasets canónicos validados.
- Unidades verificadas en 7 archivos y checksums SHA-256 conformes.
- 28 pruebas automatizadas y Ruff: PASS.

## [0.2.0] - 2026-07-18

### Added
- Caso `001_acondicionamiento_agua_lavado_pulpa_kraft`, validado, con
  simulación DWSIM, dataset, validación, QC y trazabilidad.
- Caso `002_recuperacion_vapor_flash_y_particion_de_volatiles`, en estado
  `review`, con simulación flash agua-metanol, cromatografía GC-FID sintética,
  resultados, validación, QC y procedencia.
- Figura exportada del flowsheet DWSIM del Caso 001.

### Changed
- Actualizadas la portada, el índice de casos, el roadmap y el overview para
  reflejar un portafolio con dos casos integrados.
- Estado del Caso 001 actualizado de `review` a `validated`; versión del caso
  actualizada de `0.1.0` a `0.1.1`.
- Registrada la reapertura, resolución e inspección visual del Caso 001 en
  DWSIM 9.0.5, junto con la procedencia de su figura.

### Validation
- Controles de masa, energía, unidades, metadatos, naming y checksums de los
  casos publicados: PASS.

### Notes
- Los datos y cromatogramas de los casos 001 y 002 son sintéticos y no
  representan condiciones operacionales ni información de una instalación
  industrial específica.

## [0.1.0] - 2026-05-15

### Added
- Arquitectura fundacional del repositorio PTR Engineering Cases.
- Estructura de carpetas: `docs/`, `templates/`, `schemas/`, `scripts/`,
  `data/`, `simulations/`, `notebooks/`, `dashboards/`, `cases/`,
  `assets/`, `tests/`, `references/`.
- Políticas de gobernanza: codificación, naming, unidades SI, metadata,
  checksums, versioning, lineage y provenance.
- Plantilla canónica de caso reproducible en `templates/case_template/`.
- JSON Schemas: `case_metadata`, `dataset` y `provenance`.
- Vocabularios controlados de unidades y variables.
- Scripts de automatización: `validate_metadata.py`, `validate_tables.py`,
  `compute_checksums.py`, `enforce_naming.py` y
  `unit_consistency_check.py`.
- Workflow CI `.github/workflows/validate.yml`.
- Plantillas de Pull Request y de Issue para nuevos casos.
- Licencias MIT para código y CC BY 4.0 para documentación.
- Archivos principales: `README.md`, `CONTRIBUTING.md`,
  `CODE_OF_CONDUCT.md` y `CITATION.cff`.
- Configuración Python mediante `pyproject.toml`, `requirements.txt`
  y `environment.yml`.

### Notes
- En esta versión todavía no existían casos implementados en `cases/`.
- Solo se incluía el placeholder `000_template`.
- Esta versión constituye la arquitectura base para las iteraciones posteriores.

[Unreleased]: https://github.com/robertoafn/PTR-Engineering-Cases/compare/v0.6.0...HEAD
[0.6.0]: https://github.com/robertoafn/PTR-Engineering-Cases/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/robertoafn/PTR-Engineering-Cases/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/robertoafn/PTR-Engineering-Cases/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/robertoafn/PTR-Engineering-Cases/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/robertoafn/PTR-Engineering-Cases/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/robertoafn/PTR-Engineering-Cases/releases/tag/v0.1.0
