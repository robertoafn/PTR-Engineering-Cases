# Figuras del Caso 004

| Figura | Estado | Evidencia |
|---|---|---|
| `fig_004_01_pfd_hx301_instrumentado.png` | Generada | Estados y parámetros leídos de `data/process_results_v01.csv` y `hx301_equipment_results_v01.csv`; PT, TT, FT y PDT son conceptuales. |
| `fig_004_02_sensibilidad_u_q.png` | Generada | Valores, malla y margen de presión leídos de los 12 escenarios de `data/processed/hx301_sensitivity_v01.csv`. |
| `fig_004_03_vle_meoh_h2o_dwsim_vs_dechema.png` | `NOT_RUN` | No se genera sin datos experimentales trazables y una referencia/licencia resuelta. |

Las dos figuras disponibles se regeneran con:

```bash
python cases/004_control_contaminacion_cruzada_validacion_cruzada/scripts/generate_figures.py
```

La ausencia de la tercera figura es deliberada: un gráfico vacío o sintético
podría confundirse con una validación VLE ejecutada.

El generador valida la malla, las columnas requeridas y las colisiones entre
entradas y salidas antes de escribir. Los textos numéricos no se mantienen como
constantes manuales.
