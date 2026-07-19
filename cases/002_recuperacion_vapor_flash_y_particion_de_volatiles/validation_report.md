# Informe de validación — Caso 002

## Alcance

Se evaluó el escenario base `S001`, con alimentación de 10 kg/s a 453.15 K y 1200000 Pa, expansión a 300000 Pa y separación de fases en DWSIM 9.0.5 con NRTL.

## Resultados de validación de proceso

| Control | Resultado | Criterio | Estado |
|---|---:|---:|---|
| Alimentación líquida | fracción de vapor = 0 | aproximadamente 0 | PASS |
| Residuo global de masa | `4.03E-07 %` | <= 0.01 % | PASS |
| Residuo de metanol | `9.21E-04 %` | <= 0.05 % | PASS |
| Rendimiento de vapor flash | `0.10488775` | 0 < Y < 1 | PASS |
| Recuperación de metanol al vapor | `0.42793470` | 0 < R < 1 | PASS |
| Enriquecimiento de metanol vapor/líquido | `6.38398` | > 1 | PASS |

La válvula conserva prácticamente la entalpía específica de alimentación y mezcla flash: `-1807.69489371447` frente a `-1807.69489357763 kJ/kg`; la diferencia relativa es inferior a `1E-08 %` con los valores exportados.

## Resultados de validación analítica

| Control | Resultado | Criterio | Estado |
|---|---:|---:|---|
| Blanco | sin pico detectado | sin pico significativo | PASS |
| Retención del pico MSTR-203 | 2.140 min | ventana esperada cercana a 2.14 min | PASS |
| Calibración área vs concentración de vial | R² = 0.99997113 | >= 0.995 | PASS |
| Duplicado MSTR-203 | 2.4748 % | <= 10 % | PASS |

## Limitación y tratamiento

OpenChrom 1.6.14 detectó correctamente el pico de `OC-MSTR-203` y reportó su retención y altura. Sin embargo, el reporte de pico exportado registró área `0.0` después de ejecutar el integrador trapezoidal. El área canónica se reconstruyó externamente a partir de los archivos `.xy` mediante corrección de línea base local e integración trapezoidal. El método, los límites y el origen quedan identificados en `data/chromatography_results_v01.csv`.

Por esta razón, el caso no afirma que las áreas fueron calculadas por OpenChrom. OpenChrom se reconoce como el software de importación, visualización y detección; el cálculo de área se identifica como externo y reproducible.

## Veredicto

**REVIEW.** Los controles físicos y analíticos definidos para el escenario sintético pasan, pero el caso espera la validación de schema, checksums y revisión documental final para cambiar a `validated`.
