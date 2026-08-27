# Validación de ingreso - Literature Case 102

- **Fecha:** 2026-08-09
- **Dirección actualizada:** 2026-08-26
- **Alcance:** integridad, procedencia e inspección del estado guardado
- **Veredicto:** `SOURCE_BASELINE_VERIFIED`
- **Validación científica:** `NOT_RUN`

## Criterios

| Criterio | Resultado | Estado |
|---|---:|---|
| SHA-256 y tamaño de los dos originales | 2/2 coinciden | PASS |
| Paridad con corpus FOSSEE local | 2/2 idénticos byte a byte | PASS |
| Archivo `.dwxmz` legible como ZIP/XML | 1/1 | PASS |
| Concordancia de versión | v6.5 web vs build 5.5.6886 embebido | WARNING |
| Reproducción histórica DWSIM 9.0.5/Raoult | Sin artefacto; no bloqueante | NOT_RUN |
| Dataset VLE experimental gobernado | Borrador local no promovido | NOT_RUN |
| Recálculo limpio en DWSIM estable | Sin `SimulationRun` objetivo | NOT_RUN |
| Benchmark Raoult/NRTL/UNIQUAC/M-UNIFAC | Sin resultados comparables | NOT_RUN |

## Inspección del estado guardado

La inspección de sólo lectura del XML identifica Raoult's Law, metanol, agua y
una columna de ocho etapas. Los objetos relevantes figuran calculados y sin
`ErrorMessage`. Esta evidencia describe el archivo guardado; no demuestra que
una versión actual pueda reconvergerlo sin cambios.

| Magnitud | Abstract | Estado guardado |
|---|---:|---:|
| Alimentación | 60 mol/s | 60 mol/s |
| Metanol en alimentación | 36 mol% | 36 mol% |
| Temperatura de alimentación | 300 K | 300 K |
| Alimentación precalentada | 325 K | 325.15 K |
| Relación de reflujo | 2 | 1.99995699 |
| Metanol en destilado | 90 mol% | 89.434808 mol% |
| Agua en fondos | 97 mol% | 97.803073 mol% |
| Temperatura de destilado | 340 K | 339.880120 K |
| Destilado enfriado | 298 K | 298 K |

Comprobaciones calculadas desde el estado guardado:

- balance molar global: desviación `0.000833 %`;
- balance másico global: desviación `0.002083 %`;
- balance molar de metanol: desviación `0.012487 %`;
- balance molar de agua: desviación `0.008326 %`.

Los redondeos son compatibles con el abstract, pero no equivalen a validación
experimental ni a una nueva corrida.

## Riesgos y límites

1. La ficha oficial declara DWSIM v6.5 Classic UI y el archivo declara build
   5.5.6886.34470. La discrepancia permanece abierta.
2. La atribución oficial es Rahul A S; el metadata PDF informa Rahul Nagraj.
3. Raoult representa una solución ideal. Para metanol-agua debe contrastarse
   con un modelo de coeficientes de actividad y evidencia VLE.
4. Las cuatro réplicas DWSIM 10.2.0 del autor permanecen en el workspace
   externo. Sus estados guardados no demuestran recálculo limpio ni validación
   independiente, y su etiqueta RC exacta continúa en discrepancia.
5. La extracción preliminar de Álvarez et al. requiere segunda revisión,
   decisión de derechos y reconciliación de unidades antes de promoverse.
6. La figura es un artefacto derivado de visualización, no parte del baseline
   controlado por el manifiesto.

## Regla de promoción

El caso puede publicarse como baseline fuente íntegro. No puede etiquetarse
`validated` hasta disponer de un dataset experimental gobernado, recálculos
limpios en la versión estable objetivo, balances, comparación termodinámica y
contraste externo trazable. La reproducción DWSIM 9.0.5 es histórica y
opcional; no bloquea esos gates.
