# Contributing to PTR Engineering Cases

Gracias por interesarse en este repositorio. Todo aporte debe respetar los
principios FAIR, las convenciones SI y la trazabilidad documental establecidas
en `docs/`.

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
- `references/Literature_cases_references/` es el corpus local de exploración,
  está ignorado por Git y no se publica en bloque. Nunca usar `git add -f`
  sobre esa ruta.

### Promover un caso de literatura

1. Verificar la ficha oficial, autoría, versión y licencia del caso.
2. Copiar sólo los originales necesarios a `Literature_cases/` sin
   modificarlos.
3. Registrar ruta, tamaño, SHA-256, inmutabilidad, licencia y procedencia en
   `source_manifest.json`, `checksums.sha256`, `metadata.yaml` y
   `provenance.json`.
4. Ejecutar `python scripts/validate_literature_case.py <ruta-del-caso>`; cuando
   esté disponible el corpus local, añadir `--corpus-case <ruta-fuente>` para
   comprobar igualdad binaria.
5. Mantener toda reproducción en una carpeta de variante. El archivo DWSIM
   9.0.5 que aporte el usuario y las alternativas posteriores de paquete
   termodinámico deben conservar resultados, supuestos y hashes propios; nunca
   sobrescriben el original FOSSEE.
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
- [ ] `scripts/validate_literature_case.py` retorna código 0 para el caso.

## Reglas Git

- Prohibido `force push` sobre `main`.
- Prohibido `--no-verify`.
- Tags `vX.Y.Z` firmados cuando sea posible.

## Política de datos

- No incluir datos reales sin licencia compatible.
- Etiquetar todo dataset como `synthetic`, `hypothetical`, `literature` o
  `simulated` en `metadata.yaml`.
- No reproducir literalmente material protegido (libros, papers); solo citar.
- No asumir que la licencia general del repositorio cubre artefactos de
  terceros; cada original promovido conserva la licencia declarada por su
  fuente.

## Reportar issues

Usar plantillas en `.github/ISSUE_TEMPLATE/`.

## Conducta

Se aplica el `CODE_OF_CONDUCT.md`.
