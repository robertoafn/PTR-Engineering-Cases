# Contributing to PTR Engineering Cases

Todo aporte debe respetar los principios FAIR, las convenciones SI y la
trazabilidad documental establecidas en `docs/` y `AGENTS.md`.

## Flujo de trabajo

Para el propietario del repositorio o una sesión local de ChatGPT Desktop:

```bash
git switch main
git pull --ff-only origin main
git switch -c case/NNN_slug
```

Para colaboradores externos puede utilizarse un fork antes de crear la rama.

Convenciones de ramas:

- `case/NNN_slug`: nuevo caso o ampliación sustantiva;
- `fix/<scope>`: corrección funcional;
- `docs/<topic>`: documentación y gobernanza;
- `scripts/<scope>`: automatización;
- `release/vX.Y.Z`: preparación de release.

Usar commits convencionales: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:` y
`test:`. Todo cambio se integra mediante Pull Request hacia `main`.

## Desarrollo progresivo de casos

Los casos pueden ser básicos, extensos o incorporar varios procesos. Cada caso
debe mantener un objetivo de ingeniería verificable y una frontera explícita. La
cantidad de equipos o páginas no sustituye la validación.

Para crear un caso:

1. copiar `templates/case_template/` a `cases/NNN_slug/`;
2. reemplazar todos los placeholders;
3. desarrollar la simulación, cálculos y datasets;
4. documentar supuestos, limitaciones y criterios de aceptación;
5. actualizar procedencia y checksums;
6. ejecutar el preflight antes de publicar.

## Preflight obligatorio

Caso individual:

```bash
python scripts/preflight.py cases/NNN_slug
```

Portafolio completo:

```bash
python scripts/preflight.py cases/
```

El preflight ejecuta nomenclatura, metadatos, datasets, unidades, checksums,
pruebas y linting. No abrir ni actualizar un Pull Request mientras exista un
fallo.

## Requisitos para Pull Request

- [ ] `metadata.yaml` válido.
- [ ] Cada CSV tiene sidecar `.meta.yaml` válido.
- [ ] `column` y `symbol` están mapeados correctamente en cada variable.
- [ ] Tipos, rangos, nulos, clave primaria y checksum fueron verificados.
- [ ] Unidades SI conformes al vocabulario controlado.
- [ ] `qc_checklist.md` y `validation_report.md` actualizados.
- [ ] `provenance.json` y checksums actualizados.
- [ ] Estado declarado: `draft | review | validated | published`.
- [ ] `CHANGELOG.md` actualizado en raíz y caso cuando corresponda.
- [ ] README raíz actualizado si cambia el índice, stack demostrado o roadmap.

## Estados de validación

- `draft`: desarrollo incompleto.
- `review`: artefactos completos, pendientes de cierre de validación.
- `validated`: criterios declarados superados y evidencia registrada.
- `published`: versión estable preparada para reutilización.

Para DWSIM, `validated` requiere apertura del archivo versionado, resolución del
flowsheet, revisión de topología y resultados, además de balances o cálculos
independientes. La validación realizada por el autor debe identificarse como tal
y no como reproducción independiente.

## Política de datos

- No incluir datos reales sin licencia compatible.
- No incluir datos operacionales internos o confidenciales de CMPC ni de otra
  organización.
- Etiquetar cada dataset como `synthetic`, `hypothetical`, `literature` o
  `simulated`.
- Diferenciar hechos, supuestos, estimaciones y resultados simulados.
- No reproducir literalmente material protegido; citar la fuente.

## Reglas Git

- Prohibido modificar `main` directamente.
- Prohibido `force push` sobre `main`.
- Prohibido omitir deliberadamente los controles mediante `--no-verify`.
- Si se corrige un defecto, debe añadirse una prueba de regresión.

## Reportar issues

Usar las plantillas en `.github/ISSUE_TEMPLATE/`.

## Conducta

Se aplica `CODE_OF_CONDUCT.md`.
