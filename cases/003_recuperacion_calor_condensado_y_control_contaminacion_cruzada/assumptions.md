# Supuestos del caso — 003_recuperacion_calor_condensado_y_control_contaminacion_cruzada

## 1. Condensado con metanol como mezcla binaria simplificada
- **Enunciado:** La corriente caliente se representa como una mezcla binaria de agua y metanol (trazador contaminante en baja concentración, ~639 ppm mass).
- **Justificación:** Permite modelar el comportamiento térmico del condensado industrial real de evaporadores de licor negro o del sistema de recuperación de una planta de celulosa Kraft, aislando el comportamiento del trazador volátil sin la complejidad de gases sulfurados o compuestos fenólicos.
- **Impacto si se viola:** La viscosidad, densidad y conductividad térmica variarían, afectando los coeficientes de transferencia y las caídas de presión calculadas.
- **Referencia:** Supuesto sintético/didáctico coherente con el Caso 002.

## 2. Estado estacionario
- **Enunciado:** No existe acumulación de masa ni energía.
- **Justificación:** DWSIM se ejecuta como simulación estacionaria modular secuencial.
- **Impacto si se viola:** Los transitorios operacionales (por ejemplo, arranques, paradas o variaciones de flujo) requerirían un modelo dinámico.
- **Referencia:** Documentación de DWSIM.

## 3. Pérdida de calor nula hacia el entorno
- **Enunciado:** El intercambiador de calor HX-301 se asume perfectamente aislado térmicamente (Heat Loss = 0 kW).
- **Justificación:** Facilita la verificación analítica exacta del balance térmico (Q_hot = Q_cold).
- **Impacto si se viola:** Una pérdida hacia el entorno reduciría la temperatura de salida del fluido calentado para la misma carga térmica del fluido caliente.
- **Referencia:** Ecuación clásica de balance de intercambiador.

## 4. Resistencia de ensuciamiento nula
- **Enunciado:** Los factores de ensuciamiento (Fouling Factors) para carcasa y tubos se fijan en 0 K.m²/W.
- **Justificación:** Condición ideal para representar el desempeño óptimo inicial (intercambiador limpio).
- **Impacto si se viola:** El coeficiente global de transferencia (U) disminuiría notablemente con el tiempo de operación debido a la deposición de incrustaciones o depósitos orgánicos.
- **Referencia:** Kern (1950).

## 5. Comportamiento en fase líquida monofásica
- **Enunciado:** Ambas corrientes permanecen en fase líquida (fracciones de vapor = 0.0) a lo largo de todo el intercambiador de calor.
- **Justificación:** DWSIM reporta fracción de vapor 0.0 para las corrientes resueltas con NRTL a 3.0 bar. El caso adopta ese resultado, pero no aporta una verificación independiente del punto de burbuja ni del margen de subenfriamiento.
- **Impacto si se viola:** El cambio de fase induciría coeficientes de transferencia y caídas de presión drásticamente distintos, típicos de un evaporador o condensador.
- **Referencia:** IAPWS-IF97 / NRTL.

## 6. Diferencial de presión nulo y caída de presión nula en la simulación base
- **Enunciado:** La caída de presión en el lado frío y caliente de la simulación base es de 0 Pa, y ambas corrientes operan a una presión de entrada de 300,000 Pa.
- **Justificación:** Simplificación para enfocar la simulación en el balance térmico primario. El valor $\Delta P_{clean}=0$ Pa no representa una salvaguarda ni un margen operativo.
- **Impacto si se viola:** Las pérdidas de carga y los transitorios determinan la presión local a ambos lados de una falla y pueden invertir la dirección de fuga. Una aplicación real requiere $P_{clean}>P_{contaminated}$ con margen definido y monitoreado, además de capas de detección, aislamiento o diseño.
- **Referencia:** FDA, *Heat Exchangers to Avoid Contamination*; HSE, *Heat exchangers*.
