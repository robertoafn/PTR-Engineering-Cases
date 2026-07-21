# 003_recuperacion_calor_condensado_y_control_contaminacion_cruzada — Recuperación de calor de condensado y control de contaminación cruzada

> **Status:** review  
> **Versión:** 0.1.0  
> **Aviso de datos:** entradas y resultados sintéticos o simulados.  
> **No representa condiciones operacionales reales, datos internos ni procedimientos oficiales de CMPC.**

---

## 1. Fenómeno y objetivo

El caso representa la recuperación térmica de calor sensible desde el condensado residual líquido caliente del Caso 002 (`MSTR-301_CONDENSADO_CALIENTE`, que contiene trazas contaminantes de metanol) para precalentar una corriente de agua limpia de proceso (`MSTR-302_AGUA_FRIA`). El intercambio térmico ocurre a través de una barrera física (intercambiador de carcasa y tubos).

```text
                                MSTR-301_CONDENSADO_CALIENTE (Lado Caliente / Contaminado)
                                             |
                                             v
  MSTR-302_AGUA_FRIA (Lado Frío / Limpio) ->[HX-301]-> MSTR-304_AGUA_PRECALENTADA (Lado Frío / Limpio)
                                             |
                                             v
                                MSTR-303_CONDENSADO_ENFRIADO (Lado Caliente / Contaminado)
```

El objetivo de ingeniería es:
1. Determinar la carga térmica requerida ($Q$) para precalentar el agua limpia de 293.15 K a 333.15 K utilizando el condensado caliente, y calcular la temperatura final de enfriamiento del condensado.
2. Analizar hidráulicamente el control de contaminación cruzada. Para prevenir que el metanol (contaminante) fugue hacia la corriente de agua limpia en caso de una falla en la integridad física de los tubos o uniones, se evalúa la fuerza impulsora hidráulica, requiriéndose que la presión del lado limpio sea igual o superior a la del lado caliente:
   $$\Delta P_{safety} = P_{cold} - P_{hot} \geq 0 \, \text{Pa}$$

## 2. Contexto y límites

En las plantas de celulosa Kraft, el condensado de vapor secundario (evaporadores, digestores) recupera calor hacia corrientes de agua fresca o de alimentación de calderas. Sin embargo, estos condensados suelen arrastrar impurezas volátiles de proceso como metanol y compuestos sulfurados de bajo punto de ebullición (TRS). 

El intercambiador de calor HX-301 actúa como acoplamiento térmico. La contaminación cruzada del agua limpia se controla mediante un diferencial de presiones operacionales ($\Delta P_{safety} \geq 0$), lo que garantiza que ante una rotura o poro, el agua limpia fluya hacia el condensado y no al revés.

## 3. Modelo de ingeniería

El intercambiador de calor de carcasa y tubos HX-301 se modela bajo régimen estacionario utilizando las siguientes especificaciones:

| Parámetro / Objeto | Lado Caliente (Carcasa) | Lado Frío (Tubos) |
|---|---|---|
| Fluido | Condensado (Agua + Metanol) | Agua limpia |
| Paquete Termodinámico | NRTL | NRTL |
| Flujo másico ($\dot m$) | 8.95112 kg/s | 5.00000 kg/s |
| Temperatura de entrada ($T_{in}$) | 406.649 K | 293.150 K |
| Presión de entrada ($P_{in}$) | 300000 Pa | 300000 Pa |
| Fracción másica de metanol ($w_{\text{MeOH}}$) | 0.000639089 | 0.000000000 |
| Área de intercambio ($A$) | - | 1.0 m² |
| Coeficiente global ($U$) | - | 12975.4 W/(m²·K) |
| Caída de presión ($\Delta P$) | 0 Pa | 0 Pa |

La ecuación de diseño térmico aplicada es:
$$Q = U \cdot A \cdot F \cdot \text{LMTD}$$
Donde:
- $Q$ es la carga térmica transferida.
- $\text{LMTD}$ es la diferencia de temperatura media logarítmica.
- $F$ es el factor de corrección por geometría de pases (en flujo contracorriente puro, $F = 1.0$).

## 4. Resultados principales — escenario S001

A continuación se resume la nomenclatura técnica en inglés y las propiedades físicas de las corrientes:

| Stream / Property | $T$ (K) | $P$ (Pa) | $\dot m$ (kg/s) | $\rho$ (kg/m³) | $h$ (kJ/kg) | $w_{\text{MeOH}}$ |
|---|---:|---:|---:|---:|---:|---:|
| `MSTR-301` (Hot Inlet) | 406.649 | 300000 | 8.95112 | 927.392 | -2052.33 | 0.000639089 |
| `MSTR-302` (Cold Inlet) | 293.150 | 300000 | 5.00000 | 997.599 | -2656.99 | 0.000000000 |
| `MSTR-303` (Hot Outlet) | 384.187 | 300000 | 8.95112 | 950.000 | -2171.13 | 0.000639089 |
| `MSTR-304` (Cold Outlet) | 333.150 | 300000 | 5.00000 | 982.733 | -2444.31 | 0.000000000 |

### Indicadores derivados:
- **Heat Load ($Q$):** $1063.41$ kW ($1063410$ W)
- **LMTD:** $81.9556$ K
- **Product UA:** $12.9754$ kW/K
- **Diferencial de Presión de Seguridad ($\Delta P_{safety}$):**
  $$\Delta P_{safety} = P_{\text{cold,in}} - P_{\text{hot,in}} = 300000 - 300000 = 0 \, \text{Pa}$$

## 5. Control de contaminación cruzada

El diferencial de presión $\Delta P_{safety}$ es de 0 Pa en el modelo estacionario ideal. Aunque el flujo impulsivo de fuga por diferencial de presión neto es nulo, para garantizar seguridad operacional frente a transitorios en planta real, se requiere que la presión del lado de tubos (limpio) sea controlada dinámicamente por encima del lado de carcasa ($P_{cold} > P_{hot}$). Esto asegura una dirección de fuga unidireccional de agua limpia hacia el condensado contaminado, controlando activamente el riesgo de contaminación cruzada.

## 6. Activos y reproducibilidad

1. Abrir y resolver `simulations/dwsim/003_recuperacion_calor_condensado_y_control_contaminacion_cruzada.dwxmz` en DWSIM 9.0.5.
2. Revisar la topología del flowsheet en [assets/figures/fig_003_01_flowsheet.png](assets/figures/fig_003_01_flowsheet.png).
3. Consultar `data/process_results_v01.csv` para las variables de proceso calculadas.
4. Validar los balances térmicos y de masa mediante los scripts automáticos del repositorio:
   ```bash
   python scripts/validate_metadata.py cases/003_recuperacion_calor_condensado_y_control_contaminacion_cruzada/
   python scripts/unit_consistency_check.py cases/003_recuperacion_calor_condensado_y_control_contaminacion_cruzada/
   python scripts/compute_checksums.py --verify cases/003_recuperacion_calor_condensado_y_control_contaminacion_cruzada/
   ```

## 7. Limitaciones

- No se modelan las caídas de presión dinámicas en las boquillas ni la hidráulica detallada de las tuberías.
- Los coeficientes de transferencia de calor y ensuciamiento se consideran constantes y nulos respectivamente.
- No se modelan otros compuestos volátiles reales del condensado Kraft (como TRS, metilmercaptano o dimetilsulfuro).
- La calibración física del equipo requiere de su dimensionamiento real (número de pasos, deflectores y diámetro) para comprobar el valor de $U$ calculado.

## 8. Estado

El caso se encuentra en estado `review` para la integración del portafolio.

## 9. Referencias

Ver [references.bib](references.bib).
