# AGENTS.md — Reglas operativas para agentes de código

Este archivo aplica a todo el repositorio. Debe leerse antes de crear, modificar,
validar o publicar un caso desde ChatGPT Desktop, Codex u otro agente.

## 1. Principio de trabajo

El repositorio es un portafolio profesional reproducible, no una colección de
archivos. Cada cambio debe preservar la cadena:

`fenómeno → modelo → simulación → datos → validación → trazabilidad → conclusión`

Los casos pueden ser breves o extensos y aumentar progresivamente en número de
equipos, corrientes, operaciones unitarias y procesos. La complejidad no exime el
cumplimiento del contrato documental y de QA/QC.

## 2. Antes de editar

1. Leer `README.md`, `CONTRIBUTING.md` y el README del caso afectado.
2. Revisar `git status` y no sobrescribir cambios locales ajenos al alcance.
3. Trabajar en una rama temática; nunca modificar `main` directamente.
4. Para casos nuevos usar `case/NNN_slug` y partir desde
   `templates/case_template/`.
5. Mantener identificadores estables y rutas relativas dentro del directorio del
   caso.

## 3. Contrato mínimo de cada caso

Todo caso listo para Pull Request debe incluir, según corresponda:

- `README.md` con objetivo verificable, contexto, modelo, procedimiento,
  resultados, limitaciones y conclusión;
- `metadata.yaml` válido contra `schemas/case_metadata.schema.json`;
- al menos un dataset CSV con sidecar `.meta.yaml` válido cuando existan
  resultados tabulares;
- `assumptions.md`, `validation_report.md`, `qc_checklist.md`,
  `provenance.json`, `references.bib` y `CHANGELOG.md`;
- archivo de simulación o código fuente versionado;
- checksums SHA-256 actualizados;
- datos clasificados como `synthetic`, `hypothetical`, `simulated` o
  `literature`.

En sidecars de datasets, `column` identifica la columna física del CSV y `symbol`
representa la variable científica. No asumir que ambos nombres son iguales.

## 4. Validación y estados

- `draft`: desarrollo incompleto; no implica convergencia.
- `review`: modelo y documentación completos, pendientes de validación final.
- `validated`: criterios declarados superados y evidencia registrada en
  `validation_report.md`, `qc_checklist.md` y `provenance.json`.
- `published`: versión estable, documentada y preparada para reutilización.

No declarar `validated` por inferencia. Para simulaciones DWSIM debe registrarse
la apertura del archivo versionado, resolución del flowsheet, revisión de
resultados y comparación con balances o cálculos independientes. La validación
del autor no debe describirse como reproducción independiente.

## 5. Datos y confidencialidad

- Usar únicamente datos sintéticos, hipotéticos, abiertos o licenciados.
- No incluir datos operacionales internos, propietarios o confidenciales de
  CMPC ni de otra empresa.
- Diferenciar hechos documentados, supuestos, estimaciones y resultados
  simulados.
- Usar unidades SI y nomenclatura coherente con los vocabularios del repositorio.

## 6. Regla obligatoria antes de commit o PR

Ejecutar desde la raíz:

```bash
python scripts/preflight.py cases/NNN_slug
```

Para revisar todo el portafolio:

```bash
python scripts/preflight.py cases/
```

No publicar mientras exista cualquier fallo. Si se corrige un defecto en un
script, añadir o actualizar una prueba de regresión que reproduzca el defecto.
No documentar capacidades de validación que el código todavía no implemente.

## 7. Sincronización documental

Al integrar un caso o modificar su estado:

1. actualizar el `README.md` del caso;
2. actualizar su `metadata.yaml` y `CHANGELOG.md`;
3. actualizar `provenance.json` y checksums;
4. actualizar el índice y roadmap del `README.md` raíz si corresponde;
5. actualizar el `CHANGELOG.md` raíz;
6. describir en el Pull Request qué se validó, con qué versión y qué permanece
   fuera de alcance.
