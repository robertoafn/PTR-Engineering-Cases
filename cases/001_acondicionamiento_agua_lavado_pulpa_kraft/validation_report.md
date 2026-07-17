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
- [x] Workflows `validate` y `lint` después de integrar el caso
- [x] Reapertura, resolución e inspección visual del archivo versionado por el autor

## 3. Criterios de aceptación

| Métrica | Umbral | Justificación |
|---|---:|---|
| Residuo global de masa | <= 0.01 % | Conservación |
| Residuo global de energía | <= 0.1 % | Conservación |
| Desviación de potencia hidráulica | <= 1 % | Réplica independiente |
| Desviación de carga térmica aproximada | <= 1 % | Réplica independiente |
| Fracción de vapor | aproximadamente 0 | Coherencia de fase |
| Nomenclatura | 100 % conforme | Trazabilidad |
| Reapertura y resolución | PASS | Integridad operacional del archivo versionado |
| Concordancia visual y numérica | PASS | Consistencia entre flowsheet y documentación |

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

### 4.5 Validación de ejecución por el autor

Fecha: `2026-07-17`  
Validador: Roberto Flores  
Software: DWSIM 9.0.5

Comprobaciones realizadas:

- apertura del archivo `.dwxmz` desde la ruta versionada del caso;
- resolución satisfactoria del flowsheet;
- inspección visual de la secuencia corriente de entrada → bomba → calentador → corriente de salida;
- verificación de las corrientes energéticas asociadas a bomba y calentador;
- concordancia de la potencia de bomba, aproximadamente `4.02 kW`, con el valor documentado;
- concordancia de la carga térmica, aproximadamente `1670.50 kW`, con el valor documentado.

Resultado de la validación de ejecución: **PASS**.

## 5. Análisis de residuales

Los residuales de conservación son numéricamente despreciables frente a los flujos
de energía del sistema. No se observa pérdida de masa ni inconsistencia entre las
entalpías de corriente y los deberes de los equipos.

## 6. Incertidumbre

No se desarrolla una incertidumbre metrológica completa. Las entradas son
especificaciones sintéticas deterministas. La mayor fuente de incertidumbre conceptual
es la representatividad industrial del modelo simplificado.

La validación manual confirma integridad, resolución y concordancia del archivo; no
constituye una validación contra datos operacionales reales ni un estudio de incertidumbre
experimental.

## 7. Veredicto

**PASS para el modelo numérico, las comprobaciones independientes, los controles
automatizados y la validación de ejecución realizada por el autor.**

El archivo versionado fue abierto, resuelto e inspeccionado en DWSIM 9.0.5. La
topología y los resultados principales concuerdan con la documentación. El Caso 001
cumple los criterios definidos y cambia su estado de `review` a `validated`.

## 8. Acciones no bloqueantes

1. Exportar una captura limpia del flowsheet desde DWSIM a PNG o JPG.
2. Añadir la imagen a `assets/figures/` y enlazarla desde el README del caso.
3. Actualizar la procedencia y los checksums si se incorpora un nuevo activo controlado.
4. Considerar una réplica futura por un tercero como evidencia adicional, no obligatoria.
