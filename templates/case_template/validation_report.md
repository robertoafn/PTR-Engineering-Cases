# Validation Report — <case_id>

## 1. Alcance de la validación
Qué se valida y qué no. Dominio de aplicación (rangos de T, P, x).

## 2. Estrategia
- [ ] Balance global de masa
- [ ] Balance global de energía
- [ ] Comparación contra literatura (DOI: ...)
- [ ] Paridad simulación ↔ referencia
- [ ] Réplica numérica independiente

## 3. Criterios de aceptación
| Métrica | Umbral | Justificación |
|---|---|---|
| MAE     | ≤ ... | ... |
| RMSE    | ≤ ... | ... |
| Sesgo   | |b| ≤ ... | ... |
| Balance | residuo ≤ 0.1% | Conservación |
| U95     | dentro de ... | GUM k=2 |

## 4. Resultados cuantitativos
Tabla de métricas + paridad + residuales.

## 5. Análisis de residuales
Aleatoriedad, heteroscedasticidad, sesgo sistemático.

## 6. Incertidumbre
| Fuente | Tipo (A/B) | Distribución | Contribución a u_c |
|---|---|---|---|
| ... | ... | ... | ... |

`U = k · u_c` con `k = 2` (≈ 95%).

## 7. Veredicto
**PASS | CONDITIONAL | FAIL** — justificación trazable a §3 y §4.

## 8. Acciones (si CONDITIONAL/FAIL)
Lista priorizada de correcciones antes de ascender de status.
