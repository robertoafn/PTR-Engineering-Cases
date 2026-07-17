# Validation Report — 001_acondicionamiento_agua_lavado_pulpa_kraft

## 1. Alcance de la validación

Se valida la integridad del archivo DWSIM, la convergencia estacionaria, la topología,
la nomenclatura, las condiciones de corriente, los balances globales y dos réplicas
numéricas independientes. No se valida diseño mecánico, selección comercial de bomba,
área de transferencia ni desempeño de un lavador real.

Dominio simulado:

- temperatura: 303.15–343.15 K;
- presión: 300000–600000 Pa;
- composición: agua pura;
- caudal: 10 kg/s.

## 2. Estrategia

- [x] Balance global de masa
- [x] Balance global de energía
- [x] Réplica hidráulica independiente de la bomba
- [x] Réplica calorimétrica aproximada del calentador
- [x] Verificación de rangos y fases
- [x] Inspección de paquete termodinámico y modo VLE
- [ ] Réplica en una segunda instalación independiente de DWSIM
- [ ] Revisión CI después del commit

## 3. Criterios de aceptación

| Métrica | Umbral | Justificación |
|---|---:|---|
| Residuo global de masa | <= 0.01 % | Conservación |
| Residuo global de energía | <= 0.1 % | Conservación |
| Desviación de potencia hidráulica | <= 1 % | Réplica independiente |
| Desviación de carga térmica aproximada | <= 1 % | Réplica independiente |
| Fracción de vapor | aproximadamente 0 | Coherencia de fase |
| Nomenclatura | 100 % conforme | Trazabilidad |

## 4. Resultados cuantitativos

### 4.1 Balance de masa

Entrada = 10 kg/s  
Salida = 10 kg/s  
Residuo = 0 kg/s  
Error relativo = 0 %

### 4.2 Balance de energía

```text
m_dot*h1 + W_pump + Q_heater - m_dot*h3
= -7.887455E-06 kW
```

Error relativo = `2.69E-07 %`.

### 4.3 Potencia de bomba

```text
V_dot = 0.0100427784 m^3/s
DeltaP = 300000 Pa
eta = 0.75
W_est = V_dot*DeltaP/eta = 4.01711137 kW
W_DWSIM = 4.01711137 kW
```

### 4.4 Carga térmica

```text
DeltaT = 39.96933546 K
Cp_aprox = 4.18 kJ/(kg K)
Q_est = 1670.71822 kW
Q_DWSIM = 1670.50072 kW
desviación = 0.013 %
```

## 5. Análisis de residuales

Los residuales de conservación son numéricamente despreciables frente a los flujos
de energía del sistema. No se observa pérdida de masa ni inconsistencia entre las
entalpías de corriente y los deberes de los equipos.

## 6. Incertidumbre

No se desarrolla una incertidumbre metrológica completa. Las entradas son
especificaciones sintéticas deterministas. La mayor fuente de incertidumbre conceptual
es la representatividad industrial del modelo simplificado.

## 7. Veredicto

**PASS para el modelo numérico.**

El caso se mantiene con status `review` hasta ejecutar validadores, pruebas y CI dentro
del repositorio clonado, y hasta confirmar la reapertura y resolución del archivo DWSIM
desde la copia versionada.

## 8. Acciones pendientes

1. Clonar el repositorio.
2. Copiar el caso.
3. Ejecutar validaciones locales.
4. Reabrir el archivo desde `cases/.../simulations/dwsim/`.
5. Exportar opcionalmente el flowsheet real de DWSIM a PNG.
6. Actualizar checksums si se agrega o modifica cualquier activo.
7. Abrir PR y verificar CI.
