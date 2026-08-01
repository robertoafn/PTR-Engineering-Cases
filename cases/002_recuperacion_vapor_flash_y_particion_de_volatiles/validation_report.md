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

## Revalidación automatizada con DWSIM

La resolución mediante DWSIM Automation API mantiene conformes los balances,
los controles del fenómeno y la evidencia cromatográfica. El balance energético
global entrega un residuo de `0.537716656831 %`, inferior al umbral de `1.0 %`.

Sin embargo, la corriente `MSTR-204_LIQUIDO_FLASH` presenta
`energy_flow_kW = -18349.4271015 kW` en el CSV y
`-18370.6307079 kW` al recalcular el flowsheet. La desviación máxima es
`0.115554596249 %`, superior al umbral de paridad de `0.05 %`. El hallazgo
puede corresponder a una exportación que no representa exactamente el estado
recalculado; debe investigarse y reexportarse de forma trazable antes de
promover el caso. No se modificaron el dataset ni la simulación durante esta
validación.

## Veredicto

**REVIEW — NO VALIDADO AUTOMÁTICAMENTE.** Los balances físicos, los controles
del fenómeno, los metadatos, las unidades y los checksums pasan, pero la paridad
energética entre DWSIM API y el dataset falla. El caso conserva estado `review`
hasta reconciliar esa evidencia y repetir el validador.

<!-- PTR-VALIDATION:AUTO:START -->
## Resultado automático reproducible

- **Fecha UTC:** 2026-07-26T02:39:46Z
- **Validador:** Roberto Flores Núñez
- **Versión del caso:** 0.1.2
- **Fuente solicitada:** `dwsim`
- **Fuente utilizada:** `dwsim_api`
- **Resultado general:** **FAIL**
- **Detalle de fuente:** simulación resuelta mediante DWSIM Automation API

| Criterio | Alcance | Umbral | Resultado | Estado |
|---|---|---:|---:|---|
| Metadatos, tablas, unidades y checksums | data_quality | declarativo | 0 errores | ✅ PASS |
| Paridad DWSIM API-dataset del estado de las corrientes | data_quality | <= 0.05 % | 4.86903934814e-13 % | ✅ PASS |
| Paridad DWSIM API-dataset del flujo energético | data_quality | <= 0.05 % | 0.115554596249 % | ❌ FAIL |
| Balance global de masa | numerical | <= 0.01 % | 4.03111446445e-07 % | ✅ PASS |
| Balance de masa de metanol | numerical | <= 0.05 % | 0.000920854643996 % | ✅ PASS |
| Balance global de energía del flash | numerical | <= 1.0 % | 0.537716656831 % | ✅ PASS |
| Isoentalpía entre alimentación y mezcla flash | phenomenon | <= 0.01 % | 7.56996610344e-09 % | ✅ PASS |
| Rendimiento másico de vapor flash | phenomenon | <= 1.0 dimensionless | 0.104887751939 dimensionless | ✅ PASS |
| Recuperación de metanol hacia el vapor | phenomenon | <= 1.0 dimensionless | 0.427934702295 dimensionless | ✅ PASS |
| Enriquecimiento de metanol vapor/líquido | phenomenon | > 1.0 dimensionless | 6.3839814103 dimensionless | ✅ PASS |
| Coeficiente de determinación de la calibración GC-FID | data_quality | >= 0.995 dimensionless | 0.999971130804 dimensionless | ✅ PASS |
| Diferencia relativa del duplicado GC-FID | data_quality | <= 10.0 % | 2.47482252573 % | ✅ PASS |

### Evidencia de ejecución

- Comando base: `python scripts/validate_case.py cases/002_recuperacion_vapor_flash_y_particion_de_volatiles --source dwsim`
- Resultado estructurado: `validation_results.json`

Esta sección es generada por `scripts/validate_case.py`; la narrativa técnica fuera de los delimitadores se conserva.
<!-- PTR-VALIDATION:AUTO:END -->
