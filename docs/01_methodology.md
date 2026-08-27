# 01 — Metodología

## Cadena de ingeniería

PTR aplica una metodología común a casos propios y de literatura:

```text
fuente
  → sustancia / propiedad
    → fenómeno
      → modelo
        → simulación / cálculo / experimento
          → dataset canónico
            → validación / QC
              → trazabilidad
                → interpretación
                  → decisión
```

Las últimas capas no se anticipan. Un dataset íntegro no demuestra el modelo;
un modelo convergido no demuestra exactitud experimental; y una comparación
científica no basta por sí sola para una decisión industrial.

## Principios

1. Preservar la fuente y registrar toda derivación.
2. Reproducibilidad y afirmaciones calibradas sobre espectacularidad.
3. Unidades SI y nomenclatura química explícita.
4. Transformaciones deterministas e idempotentes cuando sea posible.
5. Software, parámetros, agentes, tiempos y artefactos versionados.
6. SHA-256 para identidad e integridad; QC y validación para contenido.
7. Reutilizar schemas, vocabularios, IDs y pipelines antes de crear otros.
8. Separar evidencia, visualización y decisión.

## Artefactos por etapa

| Etapa | Artefacto principal | Control |
|---|---|---|
| Fuente | Original, referencia o especificación | Licencia, identidad, hash y cita |
| Sustancias y propiedades | IDs, composición, propiedades y unidades | Vocabulario, SI e IUPAC |
| Fenómeno | Pregunta y dominio del caso | Revisión científica |
| Modelo | Supuestos, ecuaciones, paquete y parámetros | Procedencia y aplicabilidad |
| Ejecución | `SimulationRun`, script o cuaderno reproducible | Versión, entrada/salida y logs |
| Dataset canónico | CSV/JSON y sidecar | Schema, tipos, rangos, claves y checksum |
| Validación | Especificación, resultados e informe | Métricas, tolerancias y veredicto |
| Analítica | Figura, Streamlit o futura vista Power BI | Lectura sólo desde datos gobernados |
| Decisión | Alternativas, restricciones y criterio | Lineage hasta la evidencia validada |

## Espacios de trabajo

El repositorio y el contexto local cumplen funciones distintas:

| Espacio | Uso | Política |
|---|---|---|
| `C:\PTR-DWSIM-WORK` | Investigación, simulaciones exploratorias y fuentes | Fuera de Git; no canónico |
| `references/Literature_cases_references/` | Compatibilidad con el corpus histórico | Ignorado; no usar como nueva ubicación principal |
| `cases/` | Casos PTR versionados | Contratos y validación propios |
| `Literature_cases/` | Fuentes seleccionadas y derivados auditables | Promoción explícita |

La ruta externa es contexto del mantenedor, no una dependencia portable. Un
manifiesto canónico sólo contiene rutas relativas al repositorio.

## Flujo de casos PTR

Los casos 001–004 conservan modelo, evidencia, validación y procedencia en
`cases/`. Su alcance está cerrado, pero sus estados siguen la evidencia:
001 es `validated/PASS`; 002 es `review/FAIL`; 003 y 004 son
`review/CONDITIONAL`.

Un cambio de estado exige regenerar los artefactos afectados, ejecutar los
criterios declarados y documentar la nueva derivación. No se corrige un
veredicto cambiando sólo el texto.

## Flujo de casos de literatura

1. Explorar fuentes únicamente fuera del conjunto versionado.
2. Verificar autoría, licencia, identidad, versión y relevancia.
3. Promover sólo los originales necesarios, sin modificarlos.
4. Registrar tamaño, SHA-256, fuente, licencia, discrepancias y agentes.
5. Validar la integridad con `scripts/validate_literature_case.py`.
6. Registrar cada inspección o ejecución DWSIM mediante
   [`SimulationRun`](11_simulation_run_contract.md).
7. Mantener fuente, entrada, salida, resultados y parámetros como artefactos
   separados.
8. Transformar resultados y literatura revisada en datasets canónicos.
9. Ejecutar QC estructural y después validación científica.
10. Publicar visualizaciones y decisiones como derivados, nunca como autoridad
    primaria.

La igualdad binaria acredita integridad. La reconvergencia, la paridad y la
validación requieren evidencia adicional.

## Caso 102: orden experimental

La [ADR 0001](adr/0001-dwsim-version-policy.md) asigna roles a las versiones:

- fuente histórica: build embebido 5.5.6886 y ficha FOSSEE 6.5;
- reproducción histórica opcional: DWSIM 9.0.5;
- migración exploratoria: build 10.2.0.0 con etiqueta RC no resuelta;
- objetivo reproducible: versión estable fijada por la ADR.

El trabajo actual no espera un nuevo archivo 9.0.5 como condición bloqueante.
La secuencia científica es:

1. preservar el baseline;
2. revisar y licenciar el dataset VLE experimental;
3. definir composición, presión, temperatura, unidades y parameter sets;
4. recalcular desde inicio limpio con configuración controlada;
5. comparar Raoult, NRTL, UNIQUAC y Modified UNIFAC Dortmund en la misma malla
   `T-x-y`;
6. calcular residuos y métricas para temperatura y composición de vapor;
7. evaluar después la columna completa;
8. incorporar energía, CAPEX, GHG y decisión sólo cuando sus entradas sean
   reproducibles y científicamente defendibles.

El modelo de entalpía y los parámetros binarios se controlan como factores.
Cambiar ambos a la vez impide atribuir una diferencia únicamente al paquete
termodinámico.

## Taxonomía de evidencia

`SimulationRun` usa dos ejes independientes:

| Eje | Valores |
|---|---|
| `evidence_mode` | `experimental`, `calculated`, `simulated`, `estimated`, `documentary` |
| `data_origin` | `empirical`, `literature`, `synthetic`, `hypothetical` |

El schema de datasets mantiene por compatibilidad el `source_type` legado.
La migración a los dos ejes debe ser compatible y se realizará en un cambio
separado; hasta entonces, los documentos no deben atribuir esa capacidad a
todos los sidecars.

## Criterio de promoción

Un artefacto avanza a la siguiente capa sólo cuando:

- su autoridad y procedencia están identificadas;
- sus unidades, formato, licencia e identidad son explícitos;
- la transformación puede repetirse o está documentada como manual;
- los controles aplicables tienen resultados versionados;
- las limitaciones y estados adversos permanecen visibles.

Los estados recomendados para evidencia faltante o insuficiente son
`NOT_RUN`, `NOT_DEMONSTRATED`, `CONDITIONAL` o `FAIL`, según el contrato.
No se crea un resultado positivo por ausencia de datos.
