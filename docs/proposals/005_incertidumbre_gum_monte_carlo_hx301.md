# Propuesta — Caso 005: incertidumbre GUM/Monte Carlo sobre HX-301

- **Estado:** `proposed`
- **Dependencia:** Caso 004, HX-301
- **Objetivo de versión:** posterior a v0.6.0
- **Naturaleza:** diseño reproducible de un caso; no contiene resultados de
  incertidumbre ni una validación de seguridad.

## Pregunta de ingeniería

¿Qué incertidumbre puede atribuirse a la carga térmica, la diferencia media
logarítmica de temperatura, el coeficiente global inferido y el margen de
presión de HX-301 cuando se propagan conjuntamente las incertidumbres y
correlaciones de sus magnitudes de entrada?

El caso cerrará la secuencia conceptual:

`002 flash → 003 recuperación térmica → 004 escenario corregido y validación cruzada → 005 solidez metrológica`

No se modificará el escenario versionado del Caso 004 durante la propagación.
Sus valores constituirán el punto nominal y se preservará el vínculo
conceptual con `MSTR-204_LIQUIDO_FLASH` del Caso 002 y con el escenario térmico
base del Caso 003.

## Fundamento metrológico

El método analítico seguirá [JCGM 100:2008 (GUM)](https://doi.org/10.59161/JCGM100-2008E):
definir el mensurando, formular el modelo, asignar incertidumbres estándar y
covarianzas, calcular coeficientes de sensibilidad y obtener la incertidumbre
estándar combinada. La propagación por simulación seguirá
[JCGM 101:2008](https://doi.org/10.59161/JCGM101-2008), que propaga
distribuciones mediante Monte Carlo. Como habrá varias magnitudes de salida, el
diseño considerará también [JCGM 102:2011](https://doi.org/10.59161/JCGM102-2011).

La edición vigente de las guías y la enmienda sobre no linealidad se controlarán
desde el [catálogo oficial JCGM del BIPM](https://www.bipm.org/en/publications/guides).
Si se define una regla de decisión para un margen de presión, deberá declararse
separadamente y considerar [JCGM 106:2012](https://doi.org/10.59161/JCGM106-2012);
este caso no fijará por sí solo un límite de seguridad.

## Punto nominal heredado

Los siguientes valores corresponden al punto nominal previsto por el Caso 004.
Deberán reconciliarse con su dataset versionado antes de implementar esta
propuesta; no son mediciones de planta:

| Magnitud | Valor nominal | Unidad |
|---|---:|---|
| Caudal másico, lado caliente | 8.95112 | kg/s |
| Caudal másico, lado frío | 5.00000 | kg/s |
| Temperatura caliente entrada/salida | 406.649 / 384.156 | K |
| Temperatura fría entrada/salida | 293.150 / 333.205 | K |
| Presión lado contaminado / limpio | 300000 / 350000 | Pa |
| Carga térmica DWSIM | 1064.857 | kW |
| LMTD DWSIM | 81.9121 | K |
| Área declarada | 13.0 | m² |
| Factor de corrección declarado | 1.0 | 1 |
| Coeficiente global declarado | 1000.0 | W/(m²·K) |

## Mensurandos y modelos

### Reconstrucción de desempeño

Esta ruta inferirá desempeño desde las magnitudes observables o calculadas:

\[
\dot Q_h = \dot m_h\left(h_{h,in}-h_{h,out}\right)
\]

\[
\dot Q_c = \dot m_c\left(h_{c,out}-h_{c,in}\right)
\]

\[
LMTD = \frac{\Delta T_1-\Delta T_2}
{\ln\left(\Delta T_1/\Delta T_2\right)}
\]

\[
U_{inferido}=\frac{\dot Q}{A\,F\,LMTD}
\]

Se informarán `Q_hot`, `Q_cold`, el residuo de cierre, `LMTD` y
`U_inferido`. La definición de `Q` usada para inferir `U` quedará explícita;
por ejemplo, promedio de los dos lados sólo después de verificar compatibilidad
metrológica.

### Predicción térmica

Una ruta distinta podrá usar `U`, `A`, `F` y temperaturas como entradas para
predecir:

\[
\dot Q_{UA}=U\,A\,F\,LMTD
\]

`U` no será simultáneamente entrada e inferencia en el mismo presupuesto, para
evitar circularidad y doble conteo.

### Margen hidráulico

\[
\Delta p_b=p_{limpio}-p_{contaminado}
\]

Además del valor esperado y su intervalo de cobertura se estimarán
`P(Delta p_b > 0)` y, únicamente cuando un análisis de riesgos externo defina
un margen mínimo `p_min`, `P(Delta p_b > p_min)`. El nominal de `+50000 Pa`
demuestra sólo el orden estático impuesto entre presiones. Su intervalo y la
probabilidad de mantener un margen todavía deberán calcularse; ninguna de esas
magnitudes se presentará como validación de seguridad sin una regla de decisión
externa.

## Presupuesto de incertidumbre propuesto

Antes de ejecutar el caso, cada componente deberá vincularse a resolución,
calibración, repetibilidad, especificación o estudio de propiedades. La tabla
siguiente es un **diseño inicial**, no un presupuesto aceptado:

| Entrada | Fuente a exigir | Tratamiento candidato |
|---|---|---|
| Caudales másicos | repetibilidad + certificado/especificación del medidor | Tipo A + Tipo B; normal o t según datos |
| Temperaturas de cuatro terminales | calibración, resolución, deriva y ubicación | sesgo común correlacionado + repetibilidad independiente |
| Presiones de ambos lados | calibración, resolución y dinámica del transmisor | referencia común correlacionada + ruido independiente |
| Entalpías/propiedades | paquete termodinámico y comparación con referencia | variable derivada y correlacionada con T, P y composición |
| Fracción de metanol | método analítico y muestreo | distribución acotada; correlación composicional |
| Área y factor F | planos, tolerancias y configuración | rectangular o normal según evidencia |
| Coeficiente U predictivo | datos de desempeño, ensuciamiento y regresión | distribución positiva; sólo en ruta predictiva |

No se asumirán independencia ni distribuciones normales por comodidad. Los
sesgos comunes de calibración de sensores relacionados se expresarán en una
matriz de covarianza o mediante variables latentes compartidas.

## Método GUM

Para un modelo `y=f(x)` y matriz de covarianza `U_x`:

\[
u_c^2(y)=\mathbf{c}^{T}\,\mathbf{U_x}\,\mathbf{c},\qquad
c_i=\frac{\partial f}{\partial x_i}
\]

Los coeficientes de sensibilidad se calcularán analíticamente cuando sea
razonable y por diferencias centrales verificadas en los demás casos. Se
publicarán contribuciones, covarianzas, incertidumbre estándar combinada y, si
corresponde, incertidumbre expandida `U=k*u_c` con factor y nivel de cobertura
declarados.

## Método Monte Carlo

- generador `numpy.random.Generator` con semilla versionada;
- lote inicial de 200000 realizaciones y aumento por lotes hasta convergencia;
- preservación de correlaciones mediante transformación multivariada o
  variables latentes;
- distribuciones físicamente acotadas para caudal, composición, área y `U`;
- evaluación vectorizada de cada ruta de medición;
- media, desviación estándar, intervalo de cobertura del 95 %, matriz de
  correlación de salidas y probabilidad de superar el margen;
- análisis de sensibilidad por correlación/rango o índices compatibles con el
  modelo, documentando sus limitaciones.

La convergencia se comprobará entre lotes sobre media, incertidumbre estándar y
cuantiles. El tamaño final no se justificará sólo por una cifra prefijada.

## Comparación GUM–Monte Carlo

Monte Carlo será la referencia operativa cuando la no linealidad del LMTD, las
distribuciones acotadas o la proximidad a un límite vuelvan inadecuada la
aproximación lineal. Se compararán:

- valor esperado;
- incertidumbre estándar;
- extremos del intervalo de cobertura;
- asimetría de la distribución;
- orden de contribuciones dominantes.

Los umbrales de concordancia serán declarados en `validation_spec.yaml` antes
de generar resultados. Como punto de partida sujeto a revisión: diferencia de
incertidumbre estándar relativa menor que 5 % y estabilidad de cuantiles menor
que `0.05*u_c` entre lotes finales.

## Artefactos previstos

```text
cases/005_incertidumbre_gum_monte_carlo_hx301/
├── README.md
├── metadata.yaml
├── assumptions.md
├── uncertainty_inputs.yaml
├── validation_spec.yaml
├── validation_results.json
├── validation_report.md
├── data/
│   ├── uncertainty_summary_v01.csv
│   ├── sensitivity_ranking_v01.csv
│   └── *.meta.yaml
├── assets/figures/
│   ├── fig_005_01_distribuciones_salida.png
│   └── fig_005_02_contribuciones_incertidumbre.png
└── provenance.json

scripts/run_uncertainty_hx301.py
tests/test_case_005_uncertainty.py
```

Las muestras completas de Monte Carlo no se versionarán si su tamaño es
innecesario; se conservarán semilla, parámetros, resumen, cuantiles y checksum
para regenerarlas exactamente.

## Uso de DWSIM

La DWSIM Automation API podrá resolver el punto nominal y, si el tiempo de
cómputo lo permite, un subconjunto diseñado de estados. La propagación masiva
se hará con funciones vectorizadas o un modelo sustituto verificado contra
DWSIM. Toda aproximación deberá declarar su dominio y error de sustitución.

## Criterios de aceptación propuestos

1. entradas, unidades, distribuciones, fuentes y correlaciones declaradas;
2. checksums y esquemas sin errores;
3. reproducción exacta del nominal del Caso 004 dentro del umbral fijado;
4. resultados invariantes ante repetición con la misma semilla;
5. convergencia Monte Carlo documentada por lotes;
6. comparación GUM–Monte Carlo y explicación de discrepancias;
7. ranking de contribuciones reproducible;
8. separación entre incertidumbre metrológica, incertidumbre del modelo y
   variabilidad del proceso;
9. conclusión hidráulica expresada como probabilidad condicionada al modelo,
   sin afirmar seguridad ni conformidad sin regla de decisión externa.

## Condiciones para promover la propuesta a caso

- identificar fuentes trazables para cada componente de incertidumbre;
- decidir si los valores serán sintéticos, experimentales o de especificación;
- definir mensurandos sin ambigüedad y evitar circularidad entre `Q` y `U`;
- fijar correlaciones y reglas de truncamiento antes de observar resultados;
- acordar el margen `p_min` mediante un análisis de riesgos independiente si se
  pretende evaluar conformidad hidráulica;
- implementar y probar la comparación nominal contra el Caso 004.

Hasta cumplir estas condiciones, el Caso 005 debe permanecer como propuesta y
no aparecer como caso validado en el índice automático.
