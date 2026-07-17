# NNN_slug — <title>

> **Status:** draft | review | validated | published  
> **Versión:** 0.1.0  
> **Aviso de datos:** declarar `source_type` en el sidecar del dataset  
> (`synthetic` / `hypothetical` / `simulated` / `literature`).

---

## 1. Fenómeno

Describir el fenómeno físico o químico, la escala y el régimen: laboratorio,
planta piloto o industrial-simulada; estacionario o transitorio; una o varias
fases; con o sin reacción.

## 2. Objetivo

Formular una pregunta de ingeniería única y verificable:

> Determinar X con criterio de aceptación Y, dentro del dominio Z.

## 3. Contexto industrial

Explicar la función de la operación dentro del proceso. Separar claramente el
contexto documental de cualquier dato sintético o simulado. No usar información
operacional propietaria.

## 4. Fundamento científico

Documentar ecuaciones, balances, leyes, correlaciones, supuestos termodinámicos
o cinéticos y sus regímenes de validez. Citar las fuentes en `references.bib`.

## 5. Modelo de ingeniería

Definir equipos, corrientes, especificaciones, paquete termodinámico, método de
cálculo y frontera del sistema. Justificar la selección frente a alternativas.

## 6. Supuestos

Ver `assumptions.md`.

## 7. Stack y versiones

| Componente | Versión | Licencia | Propósito |
|---|---:|---|---|
| DWSIM | x.y.z | GPL-3.0 | Simulación de proceso |
| Python | 3.12+ | PSF | Análisis y QA/QC |

Incluir únicamente herramientas utilizadas efectivamente en el caso.

## 8. Entradas

Presentar las entradas en SI y sincronizarlas con `metadata.yaml > inputs`.
Diferenciar especificaciones, supuestos y datos provenientes de fuentes.

## 9. Procedimiento reproducible

1. Abrir el archivo de simulación o ejecutar el código versionado.
2. Resolver el modelo con las versiones declaradas.
3. Generar o actualizar datasets y artefactos derivados.
4. Actualizar checksums cuando cambien los artefactos:

   ```bash
   python scripts/compute_checksums.py cases/NNN_slug
   ```

5. Ejecutar el control completo:

   ```bash
   python scripts/preflight.py cases/NNN_slug
   ```

## 10. Resultados

Presentar una tabla ejecutiva en SI y, cuando aporte valor, una figura del
flowsheet, perfiles, sensibilidad, balances o comparación con referencias.

## 11. Validación y QA/QC

Ver `validation_report.md` y `qc_checklist.md`. Incluir:

- balances y residuales;
- cálculos independientes;
- criterios de aceptación;
- sensibilidad o incertidumbre cuando corresponda;
- apertura y resolución del archivo versionado;
- identidad del validador y nivel de independencia.

## 12. Trazabilidad

Ver `provenance.json`. Los datasets deben tener sidecar `.meta.yaml`, mapeo
`column`/`symbol` y checksum SHA-256 concordante.

## 13. Limitaciones

Definir dominio de validez, fenómenos omitidos, supuestos no verificados,
incertidumbre no propagada y restricciones de uso.

## 14. Extensión industrial

Indicar qué equipos, especies, controles, datos o fenómenos serían necesarios
para evolucionar desde el caso didáctico hacia un modelo de mayor fidelidad.

## 15. Conclusión técnica

Responder directamente al objetivo, incluir las magnitudes principales y evitar
afirmaciones que excedan la evidencia disponible.

## 16. Referencias

Ver `references.bib`.
