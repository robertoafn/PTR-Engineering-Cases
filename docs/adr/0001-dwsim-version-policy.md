# ADR 0001 — Política de versiones DWSIM

- Estado: Aceptada
- Fecha: 2026-08-26
- Alcance inicial: Literature Case 102 y futuras ejecuciones DWSIM

## Contexto

El Caso 102 reúne evidencia de distintas generaciones de DWSIM que no debe
tratarse como intercambiable:

- la ficha FOSSEE declara DWSIM v6.5 Classic, mientras el archivo fuente
  contiene el build `5.5.6886.34470`; la discrepancia ya está registrada;
- el roadmap v0.6.0 reservó DWSIM `9.0.5` para una reproducción de
  referencia que todavía permanece `NOT_RUN`;
- el espacio local de investigación contiene cuatro estados guardados cuyo
  XML expone `BuildVersion` y `ProductVersion` `10.2.0.0`; el autor declara
  haberlos creado con RC1, mientras los nombres y rutas serializadas dicen
  RC12 y el registro local de instalación identifica `10.2.0-rc12`;
- la etiqueta RC exacta queda, por tanto, en discrepancia y esos estados son
  evidencia exploratoria, no recálculos limpios gobernados;
- la página oficial de descarga identifica `10.2.3`, publicada el
  2026-08-22, como versión estable vigente al aceptar esta ADR.

Cambiar de versión puede alterar propiedades, parámetros integrados,
algoritmos de flash, solver, interfaz y serialización. El documento rector
PTR Core exige, además, que cada archivo DWSIM se convierta primero en un
`SimulationRun` trazable y que los resultados no se infieran del nombre del
archivo.

## Decisión

Cada uso de DWSIM declara uno de estos roles, independientes del número de
versión:

| Rol | Versión asignada inicialmente | Uso permitido |
|---|---|---|
| `source_baseline` | build embebido `5.5.6886.34470`; ficha FOSSEE `6.5 Classic` | Preservación e inspección del original, sin sobrescribirlo |
| `reference_reproduction` | `9.0.5` | Reproducir el compromiso histórico de v0.6.0; si no se ejecuta, permanece `NOT_RUN` |
| `exploratory_migration` | build `10.2.0.0`; RC sin resolver (`RC1` declarado / `RC12` en artefactos y registro local) | Diagnóstico de migración y comparación preliminar; nunca referencia de validación |
| `target_reproducible` | `10.2.3` estable | Línea fijada para el primer recálculo gobernado del Caso 102 |

Se aplican las reglas siguientes:

1. El original promovido es inmutable. Una apertura, conversión o guardado
   produce otro artefacto con identidad y hash propios.
2. `C:\PTR-DWSIM-WORK` continúa fuera de Git. Sólo ingresan artefactos
   seleccionados después de documentar licencia, procedencia, función y
   SHA-256.
3. La versión y el modelo se leen del contenido o de evidencia explícita;
   nunca se deducen del nombre del archivo.
4. Una declaración directa del autor se registra como procedencia, pero no
   reemplaza evidencia técnica contradictoria. Hasta reconciliarla, la
   etiqueta RC no se usa en identificadores canónicos ni para concluir
   equivalencia de versión.
5. Cada combinación de escenario, paquete termodinámico, modelo de entalpía
   y parameter set genera un `SimulationRun` distinto. Un cambio NRTL ↔
   UNIQUAC, o Ideal ↔ Lee–Kesler, no es el mismo experimento.
6. Una release candidate sólo puede usar el rol `exploratory_migration` en
   el Caso 102. Un mensaje de cálculo exitoso no equivale a convergencia
   verificada, paridad ni validación científica.
7. El rol `target_reproducible` exige versión estable fijada, recálculo
   desde inicio limpio, convergencia verificada, parámetros y modelos
   explícitos, entrada y salida separadas, dataset de resultados, tiempos,
   agentes y hashes. El contrato estructural se define en
   [11 — Contrato SimulationRun](../11_simulation_run_contract.md).
8. Una versión estable posterior no sustituye silenciosamente a `10.2.3`.
   Se registra como corrida paralela y sólo reemplaza el objetivo mediante
   una ADR que explique la migración y sus pruebas de regresión.
9. Esta ADR no cambia el estado científico actual del Caso 102:
   `SOURCE_BASELINE_VERIFIED`; reproducción, paridad numérica y validación
   VLE continúan pendientes hasta producir evidencia gobernada.

## Consecuencias

- Se preserva la cadena histórica sin confundir archivo fuente, referencia,
  migración y objetivo.
- Las comparaciones entre Raoult, NRTL, UNIQUAC y Modified UNIFAC Dortmund
  podrán atribuir diferencias a configuraciones explícitas.
- El dashboard consumirá datasets y registros gobernados; no abrirá
  directamente archivos del espacio de trabajo ni extraerá semántica de
  sus nombres.
- El costo aceptado es mantener varias corridas y artefactos inmutables,
  además de ejecutar pruebas de regresión al cambiar de versión.

## Alternativas descartadas

- **Usar siempre la versión más nueva:** destruye la referencia temporal y
  vuelve móviles los resultados publicados.
- **Normalizar todo a una sola versión:** pierde evidencia histórica y puede
  sobrescribir el original.
- **Promover los estados RC como resultados:** conserva números guardados,
  pero no prueba un recálculo limpio ni separa el cambio de modelo de
  entalpía.
- **Inferir metadatos del nombre del archivo:** no es verificable y contradice
  el requisito rector de `SimulationRun`.

## Evidencia y referencias

- [Página oficial de descarga de DWSIM](https://dwsim.org/index.php/download/)
  consultada el 2026-08-26.
- [Manifiesto fuente del Caso 102](<../../Literature_cases/102 - Methanol_Water_Distillation_By_Mr_Rahul_A_S/source_manifest.json>).
- [Informe de ingreso y estado del Caso 102](<../../Literature_cases/102 - Methanol_Water_Distillation_By_Mr_Rahul_A_S/validation_report.md>).
