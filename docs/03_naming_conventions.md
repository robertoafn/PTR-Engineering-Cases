# 03 — Convenciones de Nombres

Reglas globales: minúsculas, ASCII, sin espacios, sin tildes, sin caracteres
reservados (` `, `?`, `*`, `:`, `"`, `<`, `>`, `|`).

## Patrones

| Elemento | Patrón | Ejemplo |
|---|---|---|
| Carpeta de caso | `NNN_slug_kebab` | `001_flash_binario_etanol_agua` |
| Archivo de datos | `<dominio>_<descripcion>_<version>.csv` | `vle_etoh_water_v01.csv` |
| Sidecar de dataset | `<mismo_nombre>.meta.yaml` | `vle_etoh_water_v01.meta.yaml` |
| Notebook | `NN_proposito_kebab.ipynb` | `02_calculo_K_values.ipynb` |
| Script | `verbo_objeto_snake.py` | `validate_metadata.py` |
| Figura | `fig_<caseid>_<n>_<slug>.png` | `fig_001_03_parity_plot.png` |
| Simulación DWSIM | `<case_id>.dwxmz` | `001_flash_binario.dwxmz` |

## Aplicación automática
`scripts/enforce_naming.py` verifica conformidad y falla con exit ≠ 0 en
violaciones. Se ejecuta en CI sobre cada PR.
