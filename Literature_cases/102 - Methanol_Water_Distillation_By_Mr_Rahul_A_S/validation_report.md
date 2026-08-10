# Validación de ingreso - Literature Case 102

- **Fecha:** 2026-08-09
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
| Reapertura y reconvergencia DWSIM 9.0.5/Raoult | Sin archivo del usuario | NOT_RUN |
| Comparación NRTL/UNIQUAC y VLE externo | Sin variante ni dataset externo | NOT_RUN |

## Inspección del estado guardado

La inspección de sólo lectura del XML identifica Raoult's Law, metanol, agua y
una columna de ocho etapas. Los objetos relevantes figuran calculados y sin
`ErrorMessage`. Esta evidencia describe el archivo guardado; no demuestra que
DWSIM 9.0.5 pueda reconvergerlo sin cambios.

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
4. No existe aún variante DWSIM 9.0.5 aportada por el usuario.
5. La figura es un artefacto derivado de visualización, no parte del baseline
   controlado por el manifiesto.

## Regla de promoción

El caso puede publicarse como baseline fuente íntegro. No puede etiquetarse
`validated` hasta disponer de la paridad DWSIM 9.0.5/Raoult, balances
recalculados, comparación termodinámica y contraste externo trazable.
