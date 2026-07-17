# Supuestos del caso

## 1. Agua como único componente
- **Enunciado:** La corriente se representa como agua pura.
- **Justificación:** Permite aislar los fenómenos básicos de bombeo y calentamiento.
- **Impacto si se viola:** La presencia de sales, licor negro, fibras o compuestos orgánicos modificaría densidad, viscosidad, entalpía, equilibrio de fases y demanda energética.
- **Referencia:** IAPWS-IF97 para propiedades del agua ordinaria.

## 2. Estado estacionario
- **Enunciado:** No existe acumulación de masa ni energía.
- **Justificación:** DWSIM se ejecuta como simulación estacionaria modular secuencial.
- **Impacto si se viola:** Arranques, paradas y control de temperatura requerirían un modelo dinámico.
- **Referencia:** Documentación de DWSIM.

## 3. Líquido prácticamente incompresible en la bomba
- **Enunciado:** El agua permanece líquida y su cambio de densidad durante el bombeo es pequeño.
- **Justificación:** El intervalo de presión es moderado y la temperatura está lejos de la saturación.
- **Impacto si se viola:** La aproximación V_dot*DeltaP/eta dejaría de ser suficiente.
- **Referencia:** IAPWS-IF97.

## 4. Eficiencia de bomba constante
- **Enunciado:** La eficiencia adiabática se fija en 0.75.
- **Justificación:** No se dispone de curva de fabricante; el valor es sintético y didáctico.
- **Impacto si se viola:** La potencia de eje cambia inversamente con la eficiencia.
- **Referencia:** Supuesto sintético.

## 5. Calentador ideal con eficiencia de 1.0
- **Enunciado:** La energía especificada se transfiere completamente a la corriente.
- **Justificación:** El bloque Heater representa un balance energético simplificado.
- **Impacto si se viola:** Una eficiencia menor aumentaría la demanda de utilidad.
- **Referencia:** Supuesto sintético.

## 6. Caída de presión concentrada en el calentador
- **Enunciado:** Se especifica una caída de presión de 20000 Pa y no se modelan tuberías.
- **Justificación:** El caso es introductorio y no incluye hidráulica distribuida.
- **Impacto si se viola:** La presión de salida y el requerimiento total de bombeo variarían.
- **Referencia:** Supuesto sintético.

> Los supuestos son didácticos y no representan datos operacionales de CMPC.
