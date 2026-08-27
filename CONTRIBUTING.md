# Contributing to PTR Engineering Cases

Gracias por interesarse en este repositorio. Todo aporte debe respetar los
principios FAIR, las convenciones SI y la trazabilidad documental establecidas
en `docs/`. El repositorio se trata como un sistema de ingeniería gobernado;
los agentes de código deben cumplir además [`AGENTS.md`](./AGENTS.md).

## Flujo de trabajo

1. **Fork** del repositorio.
2. Crear rama temática:
   - `case/NNN-slug` para un nuevo caso.
   - `literature/NNN-slug` para promover o reproducir un caso de literatura.
   - `docs/<topic>` para cambios en documentación normativa.
   - `scripts/<scope>` para automatización.
   - `release/vX.Y.Z` para preparación de release.
3. Hacer commits **convencionales** (`feat:`, `fix:`, `docs:`, `chore:`,
   `refactor:`, `test:`).
4. Ejecutar `python scripts/preflight.py cases/` o sobre el caso modificado.
5. Abrir Pull Request hacia `main`.
6. CI (`validate` y `lint`) debe estar **verde**.
7. Revisión y merge.

## Dos líneas de trabajo

- `cases/` contiene casos PTR desarrollados y evaluados conforme a su propia
  evidencia. En v0.6.0, 001–004 tienen alcance cerrado, pero no el mismo estado:
  001 es `validated/PASS`; 002 es `review/FAIL`; 003 y 004 son
  `review/CONDITIONAL`.
- `Literature_cases/` contiene únicamente casos externos seleccionados que ya
  recorrieron el flujo de promoción. Comienza con el Caso FOSSEE 102.
- `C:\PTR-DWSIM-WORK` es el workspace externo del mantenedor para fuentes,
  investigación y simulaciones exploratorias. Siempre permanece fuera de Git.
- `references/Literature_cases_references/` se conserva ignorado por
  compatibilidad con el corpus histórico; no es la ubicación principal para
  trabajo nuevo. Nunca usar `git add -f` para eludir esta frontera.

### Promover un caso de literatura

1. Verificar la ficha oficial, autoría, versión y licencia del caso.
2. Copiar sólo los originales necesarios a `Literature_cases/` sin
   modificarlos.
3. Registrar ruta, tamaño, SHA-256, inmutabilidad, licencia y procedencia en
   `source_manifest.json`, `checksums.sha256`, `metadata.yaml` y
   `provenance.json`.
4. Ejecutar `python scripts/validate_literature_case.py <ruta-del-caso>`; cuando
   esté disponible la fuente local, añadir `--corpus-case <ruta-fuente>` para
   comprobar igualdad binaria.
5. Mantener toda reproducción en una carpeta de variante y registrarla como
   `SimulationRun`. DWSIM 9.0.5 conserva el rol histórico de reproducción de
   referencia; el objetivo reproducible usa la versión estable fijada por la
   ADR vigente. Todas las variantes conservan resultados, parámetros,
   supuestos y hashes propios y nunca sobrescriben el original.
6. No declarar convergencia, paridad o validación científica a partir de una
   comprobación de integridad documental.

## Requisitos para PR

- [ ] `metadata.yaml` válido (si toca un caso).
- [ ] Sidecars y datasets canónicos válidos.
- [ ] Checksums actualizados en `provenance.json`.
- [ ] `validation_spec.yaml` completo y resultado reproducible revisado.
- [ ] QC checklist completado (`qc_checklist.md`).
- [ ] Status declarado: `draft | review | validated | published`.
- [ ] Naming conforme a `docs/03_naming_conventions.md`.
- [ ] Unidades SI verificadas (`scripts/unit_consistency_check.py`).
- [ ] `CHANGELOG.md` actualizado (raíz y caso si aplica).
- [ ] `python scripts/preflight.py cases/` ejecutado sin errores.

Para una PR de `Literature_cases/`, se añaden estos requisitos:

- [ ] El caso está seleccionado explícitamente; no se incluyó el corpus local.
- [ ] Originales inmutables y hashes verificados contra el manifiesto.
- [ ] Fuente, versión, autoría, licencia y discrepancias documentadas.
- [ ] Variantes separadas del original y con procedencia propia.
- [ ] El estado diferencia integridad, convergencia, paridad y validación.
- [ ] La réplica del autor y una reproducción independiente no se confunden.
- [ ] `scripts/validate_literature_case.py` retorna código 0 para el caso.

## Reglas Git

- Prohibido `force push` sobre `main`.
- Prohibido `--no-verify`.
- Tags `vX.Y.Z` firmados cuando sea posible.

## Política de datos

- No incluir datos reales sin licencia compatible.
- Etiquetar todo dataset con el `source_type` legado exigido por su schema y
  describir sin ambigüedad su origen. Para `SimulationRun`, mantener separados
  `evidence_mode` y `data_origin`; no atribuir todavía esos dos ejes a todos los
  sidecars de datasets.
- No reproducir literalmente material protegido (libros, papers); solo citar.
- No asumir que la licencia general del repositorio cubre artefactos de
  terceros; cada original promovido conserva la licencia declarada por su
  fuente.
- No promover recursos desde `C:\PTR-DWSIM-WORK` sin revisión explícita de
  derechos, identidad, procedencia y necesidad.

## Reportar issues

Usar plantillas en `.github/ISSUE_TEMPLATE/`.

## Conducta

Se aplica el `CODE_OF_CONDUCT.md`.
