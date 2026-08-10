# Roadmap v0.5.0 — Dashboard y continuidad metrológica

## Objetivo

Entregar una interfaz Streamlit reproducible que explique los fenómenos de los
casos PTR mediante preguntas, flowsheets, mecanismos, ecuaciones, datos e
interpretaciones acotadas. La validación permanece como respaldo auditable y se
deja definido el siguiente caso sobre incertidumbre de HX-301.

## Estado de los entregables

| Entregable | Estado | Evidencia |
|---|---|---|
| Descubrimiento automático de `cases/NNN_*` | Implementado | `dashboards/streamlit/data_model.py` |
| Mapa de preguntas y fenómenos | Implementado | vista `Mapa científico` |
| Estudio guiado con flowsheet y objetivos | Implementado | vista `Estudiar un caso` |
| Figuras y cálculos específicos por fenómeno | Implementado | `science_model.py` y renderizadores por caso |
| Comparación por dominio científico | Implementado | vista `Conectar fenómenos` |
| Separación de explicación y control | Implementado | vista secundaria `Rigor y fuentes` |
| Procedencia y datasets completos | Implementado | app, catálogo y resultados estructurados |
| Pruebas unitarias y recorrido Streamlit | Implementado | 11 pruebas; cuatro vistas y tres casos |
| Revisión visual en navegador | Implementado | revisión de autor, tema legible y QA estructural con AppTest |
| Preflight integral del repositorio | Implementado | 55 pruebas y todos los validadores en PASS |
| Propuesta técnica entonces numerada 004 | Implementado | Renumerada como `docs/proposals/005_incertidumbre_gum_monte_carlo_hx301.md` durante el desarrollo v0.6.0 |
| Release v0.5.0 | Implementado | tag `v0.5.0` y notas de publicación |

## Alcance funcional

### Mapa científico

- pregunta científica, flowsheet y fenómenos de cada caso;
- conclusión acotada y objetivos de aprendizaje;
- independencia material del Caso 001 y continuidad material 002 → 003;
- pregunta propuesta para 004, sin fabricar resultados de incertidumbre.

### Estudio por caso

- pregunta, objetivos y figura DWSIM con guía de lectura;
- mecanismo, ecuación, variables y significado de ingeniería;
- gráficos específicos de presión, energía, flash, partición, cromatografía,
  intercambio térmico, LMTD y presión diferencial;
- conclusión y limitaciones juntas, sin confundir coherencia computacional con
  validación experimental.

### Rigor y fuentes

- relación explícita fenómeno–criterio;
- matriz completa por alcance, incluidos resultados adversos;
- datasets, rutas y procedencia visibles;
- discrepancia API↔CSV del Caso 002 y barrera hidráulica no demostrada en HX-301
  documentadas sin convertirlas en narrativas físicas incorrectas.

## Controles de calidad para el cierre

1. ejecutar pruebas específicas y suite completa;
2. ejecutar Ruff y preflight en los tres casos;
3. levantar Streamlit en modo headless y revisar las cuatro vistas;
4. comprobar legibilidad de figuras y gráficos en resolución de escritorio;
5. confirmar que no se modificaron datasets ni simulaciones;
6. revisar enlaces Markdown y ausencia de referencias corporativas;
7. actualizar versión, changelog, citación y notas sólo al crear el release.

## Definición de terminado

v0.5.0 podrá publicarse cuando la app arranque sin excepciones, las pruebas y
el preflight pasen, las rutas funcionen desde una clonación limpia y la revisión
visual confirme que las figuras ayudan a explicar los mecanismos, que el texto
es legible y que `FAIL` o `CONDITIONAL` no inducen conclusiones físicas o de
seguridad incorrectas.

La propuesta que v0.5.0 denominaba Caso 004 no formó parte de su definición de
terminado como implementación. Durante el desarrollo v0.6.0 se renumeró como
Caso 005 para reservar el ID 004 al escenario HX-301 implementado. Este cambio
editorial no altera el cierre histórico de v0.5.0; la futura promoción de la
propuesta sigue requiriendo fuentes de incertidumbre, correlaciones, código y
resultados reproducibles.
