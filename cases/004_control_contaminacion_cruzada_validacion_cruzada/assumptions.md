# Supuestos del caso — 004_control_contaminacion_cruzada_validacion_cruzada

## 1. Continuidad conceptual con el Caso 003

- **Enunciado:** La corriente caliente usa el caudal, temperatura, presión y
  composición del escenario nominal del Caso 003, con mayor precisión
  conservada por DWSIM.
- **Justificación:** Permite evaluar el efecto de cambiar UA y el margen de
  presión sin cambiar simultáneamente el inventario térmico de entrada.
- **Impacto si se viola:** La carga y las temperaturas de salida dejarían de
  ser comparables con el Caso 003.
- **Referencia:** Caso 003, `data/process_results_v01.csv`.

## 2. Mezcla binaria sintética agua-metanol

- **Enunciado:** El lado caliente contiene agua y una fracción másica de
  metanol de `0.000639088654938267`; el lado frío es agua limpia.
- **Justificación:** Conserva el trazador utilizado en los casos 002 y 003.
- **Impacto si se viola:** Otras especies o composiciones modificarían
  propiedades, equilibrio de fases y transferencia de calor.
- **Referencia:** Supuesto didáctico de los casos 002 y 003.

## 3. Estado estacionario y pérdida de calor nula

- **Enunciado:** No existe acumulación de masa o energía y `HeatLoss = 0`.
- **Justificación:** Es la configuración guardada del flowsheet estacionario.
- **Impacto si se viola:** Los balances requerirían términos de acumulación o
  pérdida al ambiente.
- **Referencia:** Balance estacionario de energía.

## 4. Modelo global UA, no rating geométrico

- **Enunciado:** HX-301 se representa con `CalcBothTemp_UA`, contracorriente y
  `UseShellAndTubeGeometryInformation=false`.
- **Justificación:** El archivo resuelve temperaturas desde U y A sin geometría
  detallada de carcasa, tubos, pases o deflectores.
- **Impacto si se viola:** Un rating geométrico podría producir otro U, área
  efectiva, factor F y caídas de presión.
- **Referencia:** Archivo DWSIM versionado; Kern (1950).

## 5. Reparametrización circular de UA

- **Enunciado:** `U = 1000 W/(m²·K)` y `A = 13 m²` fueron seleccionados para
  obtener `UA = 13000 W/K`, muy próximo a `12975.4 W/K` del Caso 003.
- **Justificación:** Reexpresa el par U–A con un valor de U adoptado para el
  estudio y conserva aproximadamente el punto térmico; no demuestra que U sea
  correcto para un equipo real.
- **Impacto si se viola:** Usar `Q=UAFLMTD` como validación independiente
  incurriría en circularidad, porque Q depende de los mismos parámetros
  ajustados.
- **Referencia:** Definición del modelo UA y comparación con el Caso 003.

## 6. Factor de corrección igual a uno

- **Enunciado:** Se adopta `F = 1` para el modelo contracorriente idealizado.
- **Justificación:** Es la configuración guardada y permite la réplica directa
  de LMTD.
- **Impacto si se viola:** Una geometría real multipaso exigiría calcular F y
  podría reducir la fuerza impulsora térmica efectiva.
- **Referencia:** Incropera et al. (2007).

## 7. Caídas internas de presión nulas

- **Enunciado:** Las caídas de presión internas del lado caliente y frío son
  cero; el margen de 50000 Pa procede exclusivamente de las presiones de
  entrada 350000 y 300000 Pa.
- **Justificación:** Se busca aislar el signo nominal del diferencial entre
  lados.
- **Impacto si se viola:** Pérdidas de carga y transitorios podrían reducir o
  invertir el margen en el sitio de una fuga.
- **Referencia:** Configuración DWSIM; FDA y HSE.

## 8. El margen positivo no es validación de seguridad

- **Enunciado:** `ΔP_limpio > 0` sólo orienta una fuga idealizada.
- **Justificación:** El modelo no incluye falla, integridad, dinámica,
  instrumentación ni regla de decisión.
- **Impacto si se viola:** Podría comunicarse falsamente que 50000 Pa garantizan
  ausencia de contaminación o conformidad operacional.
- **Referencia:** FDA, *Heat Exchangers to Avoid Contamination*; HSE,
  *Heat Exchangers*.

## 9. Advertencia de cambio de fase

- **Enunciado:** No se asume monofase líquida perfecta en la entrada caliente;
  el archivo conserva una fracción másica de vapor cercana a `8.08×10⁻⁶` y
  mensajes de cambio de fase.
- **Justificación:** La advertencia forma parte de la evidencia guardada y
  DWSIM califica el resultado como aproximación.
- **Impacto si se viola:** Ignorarla sobrestimaría el alcance del modelo de
  calor sensible y ocultaría una posible sensibilidad al equilibrio de fases.
- **Referencia:** Archivo DWSIM versionado.

## 10. Parámetros NRTL no intercambiables

- **Enunciado:** El paquete guardado usa `alpha12 = 0.2999`; una futura tabla
  DECHEMA con `alpha = 0.2` se tratará como parametrización distinta hasta
  resolver ecuación, unidades, temperatura y procedencia.
- **Justificación:** Los parámetros NRTL dependen de la convención matemática y
  no pueden compararse sólo por su nombre.
- **Impacto si se viola:** La comparación de coeficientes de actividad podría
  ser dimensional o termodinámicamente incorrecta.
- **Referencia:** Renon y Prausnitz (1968); referencia DECHEMA pendiente.

## 11. Brecha calorimétrica independiente

- **Enunciado:** No existen mediciones experimentales de Q ni un modelo
  calorimétrico independiente del paquete de propiedades DWSIM.
- **Justificación:** Las dos cargas reconstruidas utilizan entalpías producidas
  por el mismo motor termodinámico.
- **Impacto si se viola:** El cierre energético podría interpretarse
  erróneamente como validación experimental.
- **Referencia:** Limitación declarada del caso.

## 12. Fuentes de literatura aún no resueltas

- **Enunciado:** El rango U=800–1500 W/(m²·K), los parámetros DECHEMA y los
  datos VLE no se consideran evidencia aceptada hasta disponer de referencia
  exacta, licencia y condiciones experimentales.
- **Justificación:** Las referencias numéricas `[[12]]`, `[[16]]` y `[[39]]`
  de las instrucciones no enlazan recursos del repositorio.
- **Impacto si se viola:** Se fabricaría trazabilidad y podría utilizarse
  material sin permiso o fuera de su dominio de validez.
- **Referencia:** Marcadores pendientes en `references.bib`.
