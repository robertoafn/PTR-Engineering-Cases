# 06 — Política de Validación

## Estrategias permitidas
- Balance global de masa.
- Balance global de energía.
- Comparación contra literatura (DOI obligatorio).
- Paridad simulación ↔ referencia.
- Réplica numérica independiente.

## Métricas obligatorias (cuando aplique)
- **MAE** (Mean Absolute Error).
- **RMSE** (Root Mean Square Error).
- **Sesgo relativo** (b).
- **R²** o coeficiente equivalente.
- **U95** (incertidumbre expandida con k=2 según GUM/JCGM-100).

## Reporte
Todo caso con status ≥ `validated` produce `validation_report.md` con
secciones: alcance, estrategia, criterios de aceptación, resultados,
análisis de residuales, incertidumbre, veredicto.

## Veredicto
- **PASS** — todas las métricas cumplen criterios.
- **CONDITIONAL** — cumple parcialmente; documentar condiciones.
- **FAIL** — no cumple; el caso vuelve a `draft` o `review`.

## Referencia
JCGM 100:2008 — *Evaluation of measurement data — Guide to the expression
of uncertainty in measurement* (GUM).
JCGM 101:2008 — Suplemento Monte Carlo.
