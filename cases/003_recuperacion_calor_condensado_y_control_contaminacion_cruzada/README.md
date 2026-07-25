# 003_recuperacion_calor_condensado_y_control_contaminacion_cruzada — Recuperación de calor de condensado y control de contaminación cruzada

> **Status:** review  
> **Versión:** 0.1.1<br>
> **Aviso de datos:** entradas y resultados sintéticos o simulados.  
> **No representa condiciones operacionales reales, datos propietarios ni procedimientos de una instalación específica.**

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
2. Evaluar la relación de presiones ante una pérdida hipotética de integridad. Se define:
   $$\Delta P_{clean} = P_{clean} - P_{contaminated}$$
   Para orientar una fuga desde el lado limpio hacia el contaminado se requiere
   $\Delta P_{clean} > 0$ durante todo el dominio operativo, con un margen
   mínimo definido por el análisis de riesgos, la instrumentación y los
   transitorios de la instalación. El valor $0$ Pa es solo la frontera entre
   direcciones de flujo y no constituye un margen de seguridad.

## 2. Contexto y límites

En las plantas de celulosa Kraft, el condensado de vapor secundario (evaporadores, digestores) recupera calor hacia corrientes de agua fresca o de alimentación de calderas. Sin embargo, estos condensados suelen arrastrar impurezas volátiles de proceso como metanol y compuestos sulfurados de bajo punto de ebullición (TRS). 

En la cadena conceptual del portafolio, este caso se ubica después de la
separación flash del Caso 002. Toma como base redondeada el caudal, la
temperatura, la presión y la composición de `MSTR-204` para definir `MSTR-301`;
las propiedades restantes se resuelven en el modelo del Caso 003. HX-301 transfiere calor a
agua limpia sin mezclar intencionalmente ambas corrientes. El destino posterior
del condensado enfriado y del agua precalentada queda fuera del modelo.

El intercambiador de calor HX-301 actúa como acoplamiento térmico. Una presión
mayor y monitoreada en el lado limpio puede orientar una fuga hacia el lado
contaminado, pero no sustituye la integridad mecánica ni garantiza por sí sola
la ausencia de contaminación. La evaluación real debe considerar presión local
a ambos lados de la posible falla, pérdidas de carga, arranques y paradas,
instrumentación, detección de fugas, aislamiento y alternativas como doble
placa tubular.

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
- **Diferencial limpio-contaminado ($\Delta P_{clean}$):**
  $$\Delta P_{clean} = P_{\text{clean,in}} - P_{\text{contaminated,in}} = 300000 - 300000 = 0 \, \text{Pa}$$

## 5. Control de contaminación cruzada

El modelo estacionario ideal entrega $\Delta P_{clean}=0$ Pa porque asigna
300000 Pa y caída nula a ambos lados. En esas condiciones no existe fuerza
impulsora neta en el punto idealizado, pero tampoco existe margen: una
perturbación arbitrariamente pequeña puede invertir la dirección de una fuga.
Por tanto, el escenario base **no demuestra control operacional de
contaminación cruzada**.

La aplicación industrial exigiría demostrar $P_{clean}>P_{contaminated}$ en la
ubicación de interés y durante operación normal, transitorios y fallas
consideradas, con un margen positivo específico del diseño y monitoreo del
diferencial. La presión es solo una capa. La guía FDA sobre intercambiadores con
fluidos de distinta calidad también plantea monitoreo continuo o diseños como
doble placa tubular; HSE incorpora inspección, detección de fugas, aislamiento
y análisis de modos de falla. Este caso no dimensiona ni valida esas
salvaguardas.

## 6. Activos y reproducibilidad

1. Abrir y resolver `simulations/dwsim/003_recuperacion_calor_condensado_y_control_contaminacion_cruzada.dwxmz` en DWSIM 9.0.5.
2. Revisar la topología del flowsheet en [assets/figures/fig_003_01_flowsheet.png](assets/figures/fig_003_01_flowsheet.png).
3. Consultar `data/process_results_v01.csv` para las variables de proceso calculadas.
4. Validar los balances térmicos y de masa mediante los scripts automáticos del repositorio:
   ```bash
   python scripts/validate_metadata.py cases/003_recuperacion_calor_condensado_y_control_contaminacion_cruzada/
   python scripts/validate_tables.py cases/003_recuperacion_calor_condensado_y_control_contaminacion_cruzada/
   python scripts/unit_consistency_check.py cases/003_recuperacion_calor_condensado_y_control_contaminacion_cruzada/
   python scripts/compute_checksums.py --verify cases/003_recuperacion_calor_condensado_y_control_contaminacion_cruzada/
   ```

## 7. Limitaciones

- No se modelan las caídas de presión dinámicas en las boquillas ni la hidráulica detallada de las tuberías.
- No se simula una fuga, su ubicación, su área ni su caudal; tampoco se ejecuta un análisis dinámico, HAZOP o LOPA.
- No se define un margen mínimo de presión, arquitectura de control, alarma, trip, aislamiento ni sistema de detección de fugas.
- Los coeficientes de transferencia de calor y ensuciamiento se consideran constantes y nulos respectivamente.
- No se modelan otros compuestos volátiles reales del condensado Kraft (como TRS, metilmercaptano o dimetilsulfuro).
- La calibración física del equipo requiere de su dimensionamiento real (número de pasos, deflectores y diámetro) para comprobar el valor de $U$ calculado.
- DWSIM reporta ambas corrientes como líquidas en el escenario resuelto, pero no se presenta una verificación independiente del margen respecto al punto de burbuja.

## 8. Estado

El caso se encuentra integrado en el portafolio con estado `review`. Los
balances térmicos pasan; la suficiencia de las salvaguardas contra
contaminación cruzada queda fuera del alcance demostrado.

## 9. Referencias

Ver [references.bib](references.bib).
