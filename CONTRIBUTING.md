# Contributing to PTR Engineering Cases

Gracias por interesarse en este repositorio. Todo aporte debe respetar los
principios FAIR, las convenciones SI y la trazabilidad documental establecidas
en `docs/`.

## Flujo de trabajo

1. **Fork** del repositorio.
2. Crear rama temática:
   - `case/NNN-slug` para un nuevo caso.
   - `docs/<topic>` para cambios en documentación normativa.
   - `scripts/<scope>` para automatización.
   - `release/vX.Y.Z` para preparación de release.
3. Hacer commits **convencionales** (`feat:`, `fix:`, `docs:`, `chore:`,
   `refactor:`, `test:`).
4. Ejecutar `python scripts/preflight.py cases/` o sobre el caso modificado.
5. Abrir Pull Request hacia `main`.
6. CI (`validate` y `lint`) debe estar **verde**.
7. Revisión y merge.

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

## Reglas Git

- Prohibido `force push` sobre `main`.
- Prohibido `--no-verify`.
- Tags `vX.Y.Z` firmados cuando sea posible.

## Política de datos

- No incluir datos reales sin licencia compatible.
- Etiquetar todo dataset como `synthetic`, `hypothetical`, `literature` o
  `simulated` en `metadata.yaml`.
- No reproducir literalmente material protegido (libros, papers); solo citar.

## Reportar issues

Usar plantillas en `.github/ISSUE_TEMPLATE/`.

## Conducta

Se aplica el `CODE_OF_CONDUCT.md`.
