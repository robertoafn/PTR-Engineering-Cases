# 002_recuperacion_vapor_flash_y_particion_de_volatiles — Recuperación de vapor flash y partición de compuestos volátiles

> **Status:** review  
> **Versión:** 0.1.0  
> **Aviso de datos:** entradas, cromatogramas y resultados sintéticos.  
> **No representa condiciones operacionales reales, datos internos ni procedimientos oficiales de CMPC.**

---

## 1. Fenómeno y objetivo

El caso representa un condensado caliente sintético compuesto por agua y metanol como trazador volátil. La mezcla se expande por una válvula isoentálpica y se separa en una fase vapor y una fase líquida.

```text
MSTR-201_CONDENSADO_CALIENTE
              |
              v
V-201_VALVULA_FLASH
              |
              v
MSTR-202_MEZCLA_FLASH
              |
              v
SEP-201_SEPARADOR_FLASH
         /                \
        v                  v
MSTR-203_VAPOR_FLASH    MSTR-204_LIQUIDO_FLASH
```

El objetivo es determinar el rendimiento de vapor flash y la recuperación de metanol hacia la fase vapor; además, se genera evidencia cromatográfica sintética de GC-FID para comprobar la consistencia analítica de la partición calculada.

## 2. Contexto y límites

El flujo está inspirado de manera didáctica en condensados calientes de áreas de evaporación o recuperación de una planta Kraft. No modela licor negro, fibras, sales, gases sulfurados, terpenos, ácidos orgánicos ni una composición industrial real. El metanol es únicamente un trazador sintético.

La relación con gestión energética, control de condensados y QA/QC es metodológica. No constituye una certificación, criterio regulatorio ni procedimiento de planta.

## 3. Modelo de ingeniería

| Elemento | Valor |
|---|---:|
| Simulador | DWSIM 9.0.5 |
| Paquete termodinámico | NRTL |
| Algoritmo flash | Nested Loops |
| Régimen | Estacionario |
| Alimentación | 10 kg/s; 453.15 K; 1200000 Pa |
| Fracción másica de metanol | 0.001 |
| Presión de salida de válvula | 300000 Pa |

La válvula no recibe calor ni trabajo de eje, por lo que el control físico es `h_201 ≈ h_202`.

## 4. Resultados principales — escenario S001

| Corriente | T (K) | P (Pa) | m_dot (kg/s) | w_MeOH |
|---|---:|---:|---:|---:|
| MSTR-201 | 453.150000 | 1200000 | 10.000000 | 0.001000000 |
| MSTR-202 | 406.652762 | 300000 | 10.000000 | 0.001000000 |
| MSTR-203 | 406.652762 | 300000 | 1.048878 | 0.004079930 |
| MSTR-204 | 406.652762 | 300000 | 8.951122 | 0.000639089 |

Indicadores derivados:

```math
Y_{flash}=\frac{\dot m_{203}}{\dot m_{201}}=0.10488775
```

```math
R_{MeOH,vapor}=\frac{\dot m_{MeOH,203}}{\dot m_{MeOH,201}}=0.42793470
```

```math
E_{MeOH}=\frac{w_{MeOH,203}}{w_{MeOH,204}}=6.38398
```

El vapor flash representa aproximadamente 10.49 % de la alimentación másica; recupera aproximadamente 42.79 % del metanol alimentado y está enriquecido en metanol respecto del líquido residual.

## 5. Evidencia cromatográfica

Los archivos en `data/raw/openchrom/` contienen cromatogramas sintéticos con un pico de metanol alrededor de 128.4 s. OpenChrom 1.6.14 se utilizó para importar los datos, revisar el blanco, visualizar el pico y guardar una medición nativa `.ocb` para `OC-MSTR-203`.

La detección del pico en `OC-MSTR-203` produjo `RT = 2.140 min` y altura `4201.876`. El integrador interno reportó área cero para el archivo FID importado; por transparencia, las áreas canónicas se calcularon fuera de OpenChrom por regla trapezoidal sobre el archivo `.xy`, con línea base local y límites reproducibles. Esta limitación se conserva en `validation_report.md` y `data/processed/openchrom/OC-MSTR-203_peak_report.csv`.

La calibración sintética de cinco estándares obtuvo `R² = 0.99997113`. La diferencia relativa de área entre `OC-MSTR-203` y su duplicado es `2.4748 %`.

## 6. Activos y reproducibilidad

1. Abrir y resolver `simulations/dwsim/002_recuperacion_vapor_flash_y_particion_de_volatiles.dwxmz` en DWSIM 9.0.5.
2. Consultar `data/process_results_v01.csv` y comprobar balances y fracciones de metanol.
3. Abrir los archivos `.xy` de `data/raw/openchrom/` en OpenChrom como CSD/GC-FID.
4. Usar `data/chromatography_results_v01.csv` como tabla canónica de resultados de análisis.
5. Ejecutar validaciones de metadatos y checksums según el repositorio.

## 7. Limitaciones

- La mezcla agua-metanol es un sustituto didáctico, no un condensado Kraft completo.
- Los cromatogramas se generaron sintéticamente a partir de concentraciones coherentes con el modelo.
- La importación y detección se realizaron en OpenChrom; las áreas no se atribuyen a su integrador interno.
- No existe validación experimental independiente del paquete NRTL ni de parámetros binarios.
- Los resultados no son aptos para diseño, operación o decisión industrial.

## 8. Estado

El caso queda en `review`: la simulación primaria, los datos y los controles numéricos están disponibles, pero todavía requiere una revisión final de los metadatos, checksums y trazabilidad antes de declararse `validated`.

## 9. Referencias

Ver `references.bib`.
