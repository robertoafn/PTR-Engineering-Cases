# Validation Report — 003_recuperacion_calor_condensado_y_control_contaminacion_cruzada

## 1. Alcance de la validación

Se valida la consistencia termodinámica del intercambiador de calor de carcasa
y tubos HX-301 modelado en DWSIM 9.0.5. Se verifican los balances de materia y
energía de ambas corrientes, se realiza una réplica analítica de LMTD y $Q$, y
se aplica un tamiz conceptual a la relación de presiones. No se valida la
integridad mecánica del equipo, un escenario de fuga ni un sistema industrial
de protección contra contaminación cruzada.

Dominio simulado:
- Lado caliente (condensado contaminado): 8.95112 kg/s de mezcla agua-metanol (~639 ppm mass), enfriado desde 406.649 K hasta 384.187 K a 3.0 bar.
- Lado frío (agua limpia): 5.0 kg/s de agua pura precalentada desde 293.15 K hasta 333.15 K a 3.0 bar.

## 2. Estrategia de validación

- [x] Balance de masa en el lado caliente y en el lado frío.
- [x] Balance global de energía en el intercambiador.
- [x] Réplica analítica de la diferencia de temperatura media logarítmica (LMTD).
- [x] Réplica analítica de la ecuación de diseño térmico: $Q = U \cdot A \cdot F \cdot \text{LMTD}$.
- [x] Evaluación del diferencial limpio-contaminado
  ($\Delta P_{clean}=P_{clean}-P_{contaminated}$) y de sus limitaciones.
- [x] Ejecución de pruebas de conformidad de metadatos y nomenclatura local.

## 3. Criterios de aceptación

| Métrica | Umbral | Justificación / Fuente |
|---|---:|---|
| Residuo de masa en cada lado | 0.0 % | Ley de Conservación de la Masa |
| Residuo global de energía | $\leq 0.1$ % | Ley de Conservación de la Energía (aislamiento adiabático) |
| Desviación en LMTD | $\leq 0.5$ % | Réplica analítica independiente |
| Desviación en carga térmica ($Q$) | $\leq 0.5$ % | Réplica analítica independiente frente a DWSIM |
| Diferencial limpio-contaminado ($\Delta P_{clean}$) | $>0$ Pa y margen definido por análisis de riesgos | Orientación hidráulica de una fuga hipotética; requiere monitoreo y capas adicionales |
| Nomenclatura del caso | 100% conforme | Trazabilidad del repositorio |
| Alcance del veredicto | Separado por dominio | No confundir consistencia térmica con seguridad operacional |

## 4. Resultados cuantitativos

### 4.1 Balance de masa
- Lado caliente (hot):
  - Entrada = 8.95112 kg/s
  - Salida = 8.95112 kg/s
  - Residuo = 0.0 kg/s (Error relativo: 0.0%)
- Lado frío (cold):
  - Entrada = 5.0 kg/s
  - Salida = 5.0 kg/s
  - Residuo = 0.0 kg/s (Error relativo: 0.0%)

### 4.2 Balance de energía
- Energía perdida por el lado caliente ($Q_{hot}$):
  $$Q_{hot} = \dot m_{hot} \cdot (h_{in,hot} - h_{out,hot}) = 8.95112 \, \text{kg/s} \cdot (-2052.33 - (-2171.13)) \, \text{kJ/kg} = 1063.393 \, \text{kW}$$
- Energía ganada por el lado frío ($Q_{cold}$):
  $$Q_{cold} = \dot m_{cold} \cdot (h_{out,cold} - h_{in,cold}) = 5.0 \, \text{kg/s} \cdot (-2444.31 - (-2656.99)) \, \text{kJ/kg} = 1063.400 \, \text{kW}$$
- Residuo de energía ($Q_{residue}$):
  $$Q_{residue} = Q_{hot} - Q_{cold} = 1063.393 - 1063.400 = -0.007 \, \text{kW} = -7 \, \text{W}$$
  Error relativo con respecto a la carga térmica total: $0.00066\%$ (prácticamente nulo, PASS).

### 4.3 Réplica de LMTD e Intercambio Térmico
- Temperaturas extremas en el intercambiador:
  - Extremo caliente 1: $dT_1 = T_{in,hot} - t_{out,cold} = 406.649 - 333.15 = 73.499 \, \text{K}$
  - Extremo frío 2: $dT_2 = T_{out,hot} - t_{in,cold} = 384.187 - 293.15 = 91.037 \, \text{K}$
- Diferencia de Temperatura Media Logarítmica (LMTD):
  $$\text{LMTD} = \frac{dT_2 - dT_1}{\ln(dT_2 / dT_1)} = \frac{91.037 - 73.499}{\ln(91.037 / 73.499)} = \frac{17.538}{0.213978} = 81.9615 \, \text{K}$$
  DWSIM reporta una LMTD de $81.9556 \, \text{K}$ (desviación de $0.007\%$, PASS).
- Verificación de la ecuación de diseño térmico ($Q_{calc}$):
  - $U = 12975.4 \, \text{W/(m}^2\text{K)} = 12.9754 \, \text{kW/(m}^2\text{K)}$
  - $A = 1.0 \, \text{m}^2$
  - $F = 1.0$ (flujo contracorriente puro equivalente)
  $$Q_{calc} = U \cdot A \cdot F \cdot \text{LMTD} = 12.9754 \cdot 1.0 \cdot 1.0 \cdot 81.9556 = 1063.407 \, \text{kW}$$
  El valor reportado por DWSIM es $1063.41 \, \text{kW}$ (desviación de $-0.00028\%$, PASS).

### 4.4 Tamiz de contaminación cruzada
- Presión en el lado limpio de agua fría: $P_{cold} = 300000 \, \text{Pa}$
- Presión en el lado contaminado de condensado: $P_{hot} = 300000 \, \text{Pa}$
- Diferencial limpio-contaminado:
  $$\Delta P_{clean} = P_{clean} - P_{contaminated} = 300000 - 300000 = 0 \, \text{Pa}$$

El resultado es una condición límite sin dirección hidráulica preferente ni
margen frente a incertidumbre o transitorios. No satisface el criterio robusto
$\Delta P_{clean}>0$ y, por tanto, **no demuestra** que una fuga hipotética se
oriente desde el agua limpia hacia el condensado.

Una aplicación real debe definir el margen mínimo mediante análisis de riesgos
y pérdidas de carga, medir el diferencial en puntos representativos y
considerar arranques, paradas y fallas de control. La FDA identifica el
monitoreo continuo del diferencial con mayor presión en el lado limpio o el uso
de doble placa tubular como medidas frente a contaminación por fugas. HSE
incluye además inspección, detección de fugas, aislamiento y evaluación de modos
de falla. El presente modelo no valida esas capas.

## 5. Análisis de residuales e incertidumbre

Los residuales de conservación y desviaciones analíticas son inferiores al
$0.01\%$, lo que respalda la consistencia matemática de la simulación
estacionaria dentro de la precisión publicada. Las incertidumbres conceptuales
principales son los factores de ensuciamiento nulos, la mezcla binaria, las
entalpías exportadas con precisión limitada y la ausencia de hidráulica,
dinámica y degradación mecánica. La composición real del condensado Kraft y la
deposición con el tiempo pueden reducir el coeficiente $U$.

## 6. Veredicto

- **PASS:** balances de masa y energía y réplica analítica de LMTD y carga térmica.
- **NOT DEMONSTRATED:** margen hidráulico, detección de fugas, integridad
  mecánica y control operacional de contaminación cruzada.

El caso permanece en `review`. Es reproducible como estudio térmico
estacionario y como tamiz conceptual de presión; no es una validación de diseño,
seguridad o operación industrial.

<!-- PTR-VALIDATION:AUTO:START -->
## Resultado automático reproducible

- **Fecha UTC:** 2026-07-26T02:40:27Z
- **Validador:** Roberto Flores Núñez
- **Versión del caso:** 0.1.2
- **Fuente solicitada:** `dwsim`
- **Fuente utilizada:** `dwsim_api`
- **Resultado general:** **CONDITIONAL**
- **Detalle de fuente:** simulación resuelta mediante DWSIM Automation API

| Criterio | Alcance | Umbral | Resultado | Estado |
|---|---|---:|---:|---|
| Metadatos, tablas, unidades y checksums | data_quality | declarativo | 0 errores | ✅ PASS |
| Paridad DWSIM API-dataset del estado de las corrientes | data_quality | <= 0.05 % | 0.000173345376563 % | ✅ PASS |
| Paridad DWSIM API-dataset del flujo energético | data_quality | <= 0.05 % | 0.000173345376542 % | ✅ PASS |
| Balance de masa del lado caliente | numerical | <= 0.01 % | 0 % | ✅ PASS |
| Balance de masa del lado frío | numerical | <= 0.01 % | 0 % | ✅ PASS |
| Balance de energía normalizado por la carga transferida | numerical | <= 0.1 % | 3.19190706802e-06 % | ✅ PASS |
| Desviación de la réplica analítica de LMTD | phenomenon | <= 0.5 % | 0.007 % | ✅ PASS |
| Desviación de la réplica analítica de la carga térmica | phenomenon | <= 0.5 % | 0.00028 % | ✅ PASS |
| Margen de presión limpio menos contaminado | safety | > 0.0 Pa | 0 Pa | ⚠️ NOT_DEMONSTRATED |

### Evidencia de ejecución

- Comando base: `python scripts/validate_case.py cases/003_recuperacion_calor_condensado_y_control_contaminacion_cruzada --source dwsim`
- Resultado estructurado: `validation_results.json`

Esta sección es generada por `scripts/validate_case.py`; la narrativa técnica fuera de los delimitadores se conserva.
<!-- PTR-VALIDATION:AUTO:END -->
