# 02 — Gobernanza de datos y artefactos

## Zonas de información

| Zona | Propósito | Política Git |
|---|---|---|
| `C:\PTR-DWSIM-WORK` | Contexto, fuentes y simulaciones de investigación del mantenedor | Siempre fuera del repositorio |
| `references/Literature_cases_references/` | Compatibilidad con el corpus local histórico | Ignorado; no es el workspace principal |
| `cases/` | Casos PTR desarrollados y versionados | Publicable bajo contratos del repositorio |
| `Literature_cases/` | Fuentes seleccionadas y derivados auditables | Promoción explícita y trazable |

No se incorpora un workspace completo. Cada promoción debe justificar el
artefacto y registrar licencia o derecho de uso, procedencia, identidad,
SHA-256, función y relación con otros artefactos. Nunca usar `git add -f` para
eludir esta frontera.

Las rutas absolutas locales no entran en manifests canónicos. La ausencia del
workspace externo en CI o en otro equipo no puede impedir validar el
repositorio.

## Codificación y serialización

- UTF-8 sin BOM para archivos de texto.
- Saltos de línea LF, fijados en `.gitattributes`.
- CSV con coma, decimal punto, sin separador de miles y `e` minúscula para
  notación científica.
- Fechas ISO 8601 UTC con sufijo `Z`.
- Unidades SI según [`docs/04_units_SI_policy.md`](04_units_SI_policy.md).
- Nombres e IDs según [`docs/03_naming_conventions.md`](03_naming_conventions.md).

## Datasets

El contrato vigente exige en el sidecar:
`dataset_id`, `case_id`, `title`, `description`, `source_type`,
`units`, `variables`, `created_at`, `author`, `license`, `version`,
`checksum_sha256` y `provenance_ref`.

`source_type` es un campo legado que combina conceptos. No se amplía
silenciosamente ni se interpreta como los dos ejes completos de
`SimulationRun`. Una migración posterior debe conservar compatibilidad y
separar:

- modo de evidencia: experimental, calculated, simulated, estimated o
  documentary;
- origen del dato: empirical, literature, synthetic o hypothetical.

Cada variable debe mapear símbolo, columna física, unidad y tipo. El dataset es
la frontera canónica para analítica: SQL, APIs, Streamlit, Power BI y Knowledge
Graph consumen sus IDs y valores gobernados, no extraen resultados directamente
de nombres de archivo DWSIM.

## Identidad, checksums e inmutabilidad

- SHA-256 es el algoritmo de identidad e integridad.
- Los hashes se verifican con `scripts/compute_checksums.py`.
- Un original de literatura promovido se conserva byte a byte.
- Abrir, convertir, guardar o recalcular un original genera otro artefacto con
  hash y procedencia propios.
- Una coincidencia de hash no demuestra validez científica.

Los casos de literatura enumeran además sus originales en
`source_manifest.json` y `checksums.sha256`.

## Versionado y cambios de estado

- SemVer para releases del repositorio.
- Tags Git por release.
- Keep a Changelog en `CHANGELOG.md`.
- Los cambios en desarrollo permanecen bajo `[Unreleased]` hasta aprobar el
  alcance; un roadmap no constituye una release.
- Los estados de ciclo de vida y los veredictos de validación son dimensiones
  distintas.

## Provenance y lineage

El modelo W3C PROV-lite se implementa en `provenance.json` mediante agentes,
actividades y entidades. Cada artefacto derivado identifica su fuente mediante
IDs estables y relaciones `derived_from`.

La cadena mínima de una conclusión es:

> fuente → transformación → resultado → validación → decisión

Si una transformación manual no puede automatizarse, debe registrar operador,
fecha, herramienta, versión y criterio de revisión.

## Ejecuciones DWSIM

Toda inspección o ejecución usada como evidencia se registra con el
[contrato `SimulationRun`](11_simulation_run_contract.md) y se valida contra
[`schemas/simulation_run.schema.json`](../schemas/simulation_run.schema.json).
La [ADR 0001](adr/0001-dwsim-version-policy.md) fija los roles iniciales de
versión para el Caso 102.

- Un estado guardado se declara como inspección sin recálculo.
- Un mensaje de éxito no equivale a convergencia verificada.
- Fuente, entrada, salida, parámetros, resultados y logs son artefactos
  distintos cuando existen.
- Una réplica realizada por el autor no se denomina reproducción independiente.
- Cambiar paquete, parameter set o modelo de entalpía genera otro
  `SimulationRun`.

## Vistas analíticas y semánticas

Streamlit es la vista científica implementada actualmente. SQL, Power BI,
JSON-LD y Knowledge Graph son capas objetivo. Para incorporarlas deben:

1. consumir artefactos canónicos;
2. conservar IDs, unidades, versiones y lineage;
3. ser regenerables;
4. no introducir hechos sin fuente;
5. demostrar un consumidor o decisión concreta.

## Agentes de código

Las reglas persistentes para Codex y otros agentes están en
[`AGENTS.md`](../AGENTS.md). Todo agente debe reutilizar contratos existentes,
mantener `C:\PTR-DWSIM-WORK` fuera de Git, calibrar las afirmaciones y ejecutar
validaciones proporcionales al riesgo antes de publicar una PR.
