# 08 — Licenciamiento

| Componente | Licencia | Archivo |
|---|---|---|
| Código (`scripts/`, `tests/`, notebooks ejecutables) | **MIT** | `LICENSE` |
| Documentación (`docs/`, `README`, `cases/**/*.md`) | **CC BY 4.0** | `LICENSE-docs` |
| Datos sintéticos generados | **CC0 1.0** | declarado por dataset |
| Datos derivados de literatura | Hereda licencia de fuente | declarado por dataset |
| Software de terceros | Conserva su licencia | declarado en `metadata.yaml` |
| Artefactos FOSSEE promovidos | Conserva la licencia indicada por la fuente | `source_manifest.json`, `metadata.yaml` y `provenance.json` |

## Política de terceros
- No incluir binarios propietarios.
- No reproducir tablas/figuras de papers; **citar y enlazar al DOI**.
- Libros y manuales: solo referencia bibliográfica en
  `references/bibliography.bib`.
- Ejercicios inspirados en libros: reformular fenómeno, declarar fuente,
  no copiar literalmente el enunciado.

## Casos FOSSEE

- `C:\PTR-DWSIM-WORK` es el workspace externo del mantenedor y nunca se
  distribuye en bloque desde este repositorio. La ruta interna
  `references/Literature_cases_references/` permanece ignorada sólo por
  compatibilidad histórica.
- Sólo se publica en `Literature_cases/` un caso seleccionado después de
  verificar su ficha oficial, autoría, licencia y procedencia.
- Cada original conserva su licencia de origen. La licencia general del código
  o de la documentación PTR no reemplaza ni amplía esa licencia.
- Los originales se mantienen inmutables y con SHA-256. Adaptaciones, figuras,
  metadatos y variantes deben distinguir su autoría y licencia de la fuente.
- El Caso 102 registra la licencia indicada por su ficha FOSSEE en sus propios
  metadatos; futuros casos se revisan individualmente y no heredan esa
  conclusión de forma automática.
- Si la licencia o atribución de un artefacto no puede verificarse, el archivo
  no se promueve: se conserva únicamente como referencia local o se enlaza a
  la fuente.

## Datos extraídos de literatura

- La posibilidad técnica de transcribir una tabla no concede derechos de
  redistribución.
- Antes de promover observaciones experimentales se documentan cita, DOI,
  licencia o base legal, alcance de la extracción y revisión de transcripción.
- Cuando no sea posible distribuir la tabla, se versionan el schema, el
  procedimiento de extracción y las métricas permitidas, y se mantiene la
  fuente fuera de Git.
- Los valores normalizados conservan vínculo con el valor publicado, unidad
  original, transformación y advertencias. Corregir una unidad aparente sin
  conservar el dato fuente destruye auditabilidad.

## Exclusiones de copyright
- Logos y marcas de terceros: no incluir salvo permiso explícito.
- Capturas de pantalla de software propietario: solo fair use técnico
  mínimo y declarado.
