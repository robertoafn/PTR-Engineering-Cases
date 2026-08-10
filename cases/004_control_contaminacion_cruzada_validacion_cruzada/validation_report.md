# Validation Report — 004_control_contaminacion_cruzada_validacion_cruzada

## 1. Alcance de la validación

Se evalúa la coherencia numérica del punto nominal de HX-301 guardado en DWSIM
9.0.5: estados de cuatro corrientes, balances por lado, carga térmica, LMTD,
especificación UA y diferencial de presión limpio-contaminado. La Automation
API resolvió una copia temporal, extrajo los cinco objetos solicitados y
confirmó que el archivo de origen permaneció inalterado.

No se validan el rating geométrico del intercambiador, un coeficiente U medido,
una calorimetría experimental, una fuga, integridad mecánica, dinámica,
instrumentación, seguridad operacional ni conformidad regulatoria.

Dominio nominal:

- lado caliente: 8.951122 kg/s de agua-metanol, 406.649350 K y 300000 Pa;
- lado frío: 5 kg/s de agua, 293.15 K y 350000 Pa;
- `U = 1000 W/(m²·K)`, `A = 13 m²`, `F = 1`;
- caídas internas de presión iguales a cero.

## 2. Estrategia

- [x] Verificación de convergencia y no modificación de la fuente mediante API.
- [x] Balance de masa en los lados caliente y frío.
- [x] Balance de energía entre ambos lados.
- [x] Réplica independiente de LMTD con temperaturas terminales.
- [x] Comprobación del cierre `Q=UAFLMTD`, identificando su circularidad.
- [x] Evaluación nominal del margen limpio-contaminado.
- [x] Inspección de advertencias y del modo de cálculo guardado.
- [x] Sensibilidad de U y caudal frío reproducida mediante API.
- [ ] Comparación NRTL contra una referencia DECHEMA resuelta.
- [ ] Comparación VLE contra datos experimentales trazables.
- [ ] Comparación calorimétrica independiente.
- [ ] Cierre de la discrepancia energética API↔dataset del Caso 002.

## 3. Criterios de aceptación

| Métrica | Umbral | Alcance |
|---|---:|---|
| Balance de masa por lado | ≤ 0.01 % | Conservación numérica |
| Residuo de energía respecto de Q | ≤ 0.01 % | Conservación numérica |
| Diferencia absoluta de LMTD | ≤ 0.1 K | Réplica analítica |
| Cierre de la especificación UA | ≤ 0.5 % | Consistencia, no validación independiente |
| Margen limpio-contaminado | > 0 Pa | Signo hidráulico nominal |
| Fracción de vapor de entrada | = 0 | Hipótesis monofásica |
| Sensibilidad U/caudal | 12 escenarios válidos | Ejecutada: 12/12 |
| Coeficientes NRTL vs. DECHEMA | ≤ 0.5 % | Pendiente de fuente y ejecución |
| VLE vs. literatura | ≤ 0.01 K, preliminar | Pendiente de fuente y revisión del umbral |
| Composición VLE vs. literatura | ≤ 0.01 fracción molar | Pendiente de fuente y revisión del umbral |
| Paridad final del Caso 002 | ≤ 0.05 % | FAIL: 0.115554596 % |

El margen positivo no es un criterio de seguridad suficiente. La aplicación
real necesita un margen mínimo definido por análisis de riesgos y conservado en
operación normal, transitorios y fallas consideradas.

## 4. Resultados cuantitativos verificados

### 4.1 Estados de corriente

| Objeto | T, K | P, Pa | ṁ, kg/s | h, kJ/kg |
|---|---:|---:|---:|---:|
| `MSTR-301_CONDENSADO_CALIENTE` | 406.649349771 | 300000 | 8.951122 | -2052.326970301 |
| `MSTR-302_AGUA_FRIA` | 293.150000000 | 350000 | 5.000000 | -2656.953827028 |
| `MSTR-303_CONDENSADO_ENFRIADO` | 384.156247979 | 300000 | 8.951122 | -2171.290465943 |
| `MSTR-304_AGUA_PRECALENTADA` | 333.204676360 | 350000 | 5.000000 | -2443.982476663 |

Las temperaturas de entrada efectivas son 406.64935 y 293.15 K. Los valores
preliminares 453.15 y 303.15 K no describen el archivo finalmente entregado y
no deben usarse para reconstruir este resultado.

### 4.2 Balances de masa y energía

Los caudales de entrada y salida son idénticos en cada lado:

- caliente: `8.951122 - 8.951122 = 0 kg/s`;
- frío: `5 - 5 = 0 kg/s`.

Usando las entalpías extraídas:

\[
Q_h=8.951122[-2052.326970301-(-2171.290465943)]
=1064.856763040\;\text{kW}
\]

\[
Q_c=5[-2443.982476663-(-2656.953827028)]
=1064.856751827\;\text{kW}
\]

El residuo es `0.000011214 kW`, equivalente a aproximadamente
`1.05×10⁻⁶ %` de la carga media. Cumple el criterio numérico, pero ambas
entalpías proceden del mismo motor DWSIM: no cierra la brecha calorimétrica
independiente.

### 4.3 LMTD y cierre UA

Las diferencias terminales reconstruidas son:

\[
\Delta T_1=406.649349771-333.204676360=73.444673410\;K
\]

\[
\Delta T_2=384.156247979-293.15=91.006247979\;K
\]

La réplica entrega `LMTD = 81.911940174 K`; DWSIM reporta
`81.912058696 K`. La diferencia absoluta es `0.000118522 K`, dentro del
umbral.

Con el LMTD reconstruido:

\[
Q_{UA}=1000\times13\times1\times81.911940174
=1064.855222260\;\text{kW}
\]

La diferencia relativa frente a Q DWSIM es aproximadamente `0.0001447 %`.
Este cierre era esperable porque el Caso 004 conserva casi el mismo UA del Caso
003: `13000 W/K` frente a `12975.4 W/K`. No constituye validación independiente
del valor de U ni del área.

### 4.4 Margen de presión

\[
\Delta P_{limpio}=350000-300000=50000\;\text{Pa}
\]

El signo es positivo y las caídas internas configuradas son cero. Esto
demuestra únicamente el escenario nominal de entradas. No se calculan presiones
locales en una falla, incertidumbre, pérdidas externas ni desempeño transitorio.

### 4.5 Sensibilidad de U y caudal frío

Se resolvieron 12/12 escenarios con
`U={800, 1000, 1200, 1500} W/(m²·K)` y factores de caudal frío
`{0.8, 1.0, 1.2}`. La carga aumentó monótonamente con ambas variables:

- intervalo de Q: `867.678324–1461.455133 kW`;
- caso nominal S005: `1064.856763 kW`;
- margen limpio-contaminado: `+50000 Pa` en los 12 escenarios;
- máximo residuo energético relativo: `7.2986×10⁻⁵ %`.

La tendencia es coherente con el modelo UA: un U mayor intensifica la
transferencia y un mayor caudal frío eleva la capacidad térmica de ese lado.
Este barrido verifica respuesta y reproducibilidad del modelo; no valida el
rango de U contra literatura ni elimina la circularidad del punto nominal.

### 4.6 Tamiz calorimétrico entre casos

La respuesta del lado de agua fría implica una capacidad calorífica efectiva:

\[
c_{p,ef,004}=
\frac{1064.856752}
{5(333.204676-293.15)}=5.31702\;\text{kJ/(kg·K)}
\]

Como referencia interna, el Caso 001 con Steam Tables/IAPWS implica
`4.17946 kJ/(kg·K)` en su intervalo 303.18–343.15 K. El valor efectivo del
Caso 004 es aproximadamente 27.22 % mayor. Las presiones, intervalos y paquetes
no son idénticos, de modo que esta comparación no demuestra por sí sola un
error; sí identifica una sensibilidad material a las propiedades y justifica
mantener la calorimetría independiente en `NOT_RUN` hasta ejecutar un
contraste IAPWS/experimental bajo las mismas condiciones.

### 4.7 Paridad DWSIM API–dataset del Caso 002

El script `parity_check_002.py` reabrió una copia del `.dwxmz` del Caso 002 y
comparó cada corriente con su dataset publicado. El SHA-256 de la simulación
fuente permaneció inalterado.

- máxima diferencia de estado: `4.869039348×10⁻¹³ %` (`PASS`);
- máxima diferencia de energía: `0.115554596 %` (`FAIL`);
- tolerancia por alcance: `0.05 %`;
- comparación que falla: `MSTR-204_LIQUIDO_FLASH.energy_flow_kW`.

El resultado no invalida por sí solo la explicación del flash o la partición,
pero impide declarar cerrada su reproducibilidad energética. En el Caso 004 se
trata como dependencia externa no bloqueante: el criterio muestra `FAIL`, el
veredicto global continúa `CONDITIONAL` y los casos 002/003 no se promueven.

## 5. Advertencias y residuales cualitativos

El archivo contiene mensajes persistidos de `Phase change in hot stream
detected` y señala que el resultado del intercambio es una aproximación. La
entrada caliente conserva una fracción másica de vapor cercana a
`8.08094×10⁻⁶`; por tanto, el criterio de monofase líquida estricta queda
`NOT_DEMONSTRATED`.

Una ejecución preliminar expuso una resolución incompleta de la dependencia
ThermoCS en el runner. La implementación final localizó esa dependencia,
resolvió el flowsheet NRTL, extrajo los objetos solicitados y conservó el
checksum de la fuente. Esta incidencia de infraestructura queda en la
trazabilidad histórica; no se presenta como advertencia física de la ejecución
final.

## 6. Incertidumbre y brechas de evidencia

No existe todavía un presupuesto GUM/Monte Carlo. Tampoco se dispone de:

- repetibilidad o calibración de temperaturas, presiones y caudales;
- incertidumbre del área, U o factor F;
- calorimetría experimental independiente;
- parámetros DECHEMA con referencia, licencia, unidades y convención
  matemática resueltas;
- datos VLE experimentales versionados;
- validación de la pequeña fracción vapor y del margen de subenfriamiento;
- análisis de incertidumbre o riesgo para el margen de 50000 Pa.

El paquete DWSIM guarda `alpha12 = 0.2999`. La propuesta de usar `alpha = 0.2`
no puede presentarse como paridad hasta especificar y validar la
parametrización DECHEMA correspondiente.

## 7. Veredicto

**CONDITIONAL.** El punto nominal converge y cumple balances, LMTD y signo del
margen hidráulico. El resultado permanece condicionado por:

1. la advertencia de cambio de fase;
2. el carácter circular de la reparametrización UA;
3. la ausencia de calorimetría independiente;
4. las comparaciones DECHEMA y VLE no ejecutadas;
5. el `FAIL` reproducido de paridad energética del Caso 002:
   `0.115554596 % > 0.05 %`.

El ciclo de vida correcto es `review`. No se promueven los casos 002 o 003 y no
se declara validación de seguridad.

## 8. Acciones para cerrar el caso

1. Resolver las referencias y licencias DECHEMA, U y VLE.
2. Ejecutar las comparaciones independientes y revisar los umbrales antes de
   observar los resultados.
3. Reconciliar `MSTR-204.energy_flow_kW` en el Caso 002 y regenerar su
   resultado estructurado sin alterar la tolerancia.
4. Mantener `CONDITIONAL` ante cualquier criterio requerido `NOT_RUN` o
   `NOT_DEMONSTRATED`.

El resultado estructurado y la sección automática PTR se generan exclusivamente
mediante `scripts/validate_case.py --write-artifacts`.

<!-- PTR-VALIDATION:AUTO:START -->
## Resultado automático reproducible

- **Fecha UTC:** 2026-08-02T06:48:18Z
- **Validador:** Roberto Flores Núñez
- **Versión del caso:** 0.1.0
- **Fuente solicitada:** `dwsim`
- **Fuente utilizada:** `dwsim_api`
- **Resultado general:** **CONDITIONAL**
- **Detalle de fuente:** simulación resuelta mediante DWSIM Automation API

| Criterio | Alcance | Umbral | Resultado | Estado |
|---|---|---:|---:|---|
| Metadatos, tablas, unidades y checksums | data_quality | declarativo | 0 errores | ✅ PASS |
| Paridad DWSIM API-dataset del estado de las corrientes | data_quality | <= 0.01 % | 5.53941157363e-13 % | ✅ PASS |
| Balance de masa del lado caliente | numerical | <= 0.01 % | 0 % | ✅ PASS |
| Balance de masa del lado frio | numerical | <= 0.01 % | 0 % | ✅ PASS |
| Balance de energia normalizado por la carga transferida | numerical | <= 0.01 % | 1.0530736408e-06 % | ✅ PASS |
| Diferencia absoluta entre LMTD DWSIM y replica independiente | phenomenon | <= 0.1 K | 0.000118521668995 K | ✅ PASS |
| Cierre numerico de Q mediante U por A por F por LMTD | phenomenon | <= 0.5 % | 0.000144691563344 % | ✅ PASS |
| Signo nominal del margen de presion limpio menos contaminado | phenomenon | > 0.0 Pa | 50000 Pa | ✅ PASS |
| Ausencia de fase vapor en la entrada caliente | phenomenon | <= 0.0 dimensionless | 8.08093885494e-06 dimensionless | ⚠️ NOT_DEMONSTRATED |
| Comparacion contra calorimetria independiente | phenomenon | <= 0.01 % | N/A | ⏸ NOT_RUN |
| Sensibilidad reproducible de U y caudal frio | phenomenon | >= 12.0 dimensionless | 12 dimensionless | ✅ PASS |
| Coeficientes de actividad NRTL frente a DECHEMA | data_quality | <= 0.5 % | N/A | ⏸ NOT_RUN |
| Curva VLE DWSIM frente a datos experimentales | data_quality | <= 0.01 K | N/A | ⏸ NOT_RUN |
| Composicion VLE DWSIM frente a datos experimentales | data_quality | <= 0.01 dimensionless | N/A | ⏸ NOT_RUN |
| Paridad final DWSIM API-dataset del Caso 002 | data_quality | <= 0.05 % | 0.115554596249 % | ❌ FAIL |

### Evidencia de ejecución

- Comando base: `python scripts/validate_case.py cases/004_control_contaminacion_cruzada_validacion_cruzada --source dwsim`
- Resultado estructurado: `validation_results.json`

Esta sección es generada por `scripts/validate_case.py`; la narrativa técnica fuera de los delimitadores se conserva.
<!-- PTR-VALIDATION:AUTO:END -->
