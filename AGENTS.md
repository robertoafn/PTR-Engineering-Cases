# Instrucciones para agentes de código

## Alcance

Estas reglas aplican a todo el repositorio. Los documentos más específicos de
un subdirectorio pueden añadir restricciones, pero no relajar la gobernanza,
la trazabilidad ni la separación de evidencia definidas aquí.

## Misión

Tratar PTR Engineering Cases como un **sistema de ingeniería gobernado**, no
como una colección de scripts ni como un depósito de simulaciones. Cada cambio
debe fortalecer, de forma verificable, la cadena:

> elementos → sustancias → propiedades → fenómenos → modelos → simulación →
> evidencia experimental → proceso → energía → ambiente → economía →
> supply chain → decisión industrial

El objetivo es aumentar conocimiento técnico reutilizable. Añadir archivos,
tecnologías o abstracciones no es progreso si no mejora reproducibilidad,
interoperabilidad, validación o capacidad de decisión.

## Fuentes de autoridad

1. La solicitud explícita del mantenedor define el objetivo inmediato.
2. Los schemas, ADR, pruebas y documentos versionados definen los contratos
   vigentes y el comportamiento comprobable del repositorio.
3. En el equipo del mantenedor, `C:\PTR-DWSIM-WORK` es el espacio externo de
   investigación. El documento
   `Deepresearch y referencias para siguientes pasos/Prototipo PTR Core .md`
   guía la evolución arquitectónica, pero no convierte por sí solo una idea en
   capacidad implementada.
4. Si una fuente entra en conflicto con evidencia técnica, registrar la
   discrepancia; no elegir silenciosamente la versión más conveniente.

La ausencia de `C:\PTR-DWSIM-WORK` en otro entorno no debe impedir validar el
repositorio. Ninguna ruta absoluta local puede formar parte de un manifiesto
canónico.

## Espacio externo y promoción

- `C:\PTR-DWSIM-WORK` permanece fuera de Git y se usa como contexto de sólo
  lectura salvo instrucción explícita del mantenedor.
- Nunca incorporar esa carpeta en bloque ni usar `git add -f` para eludir una
  exclusión.
- Promover únicamente artefactos seleccionados con licencia o derecho de uso,
  identidad, SHA-256, procedencia, función, formato y revisión documentados.
- Conservar las fuentes promovidas como inmutables. Una conversión, apertura y
  guardado o recálculo genera un artefacto nuevo.

## Principios de diseño

- Preservar y reutilizar el legado compatible antes de crear estructuras
  paralelas.
- Preferir transformaciones deterministas, idempotentes y ejecutables sobre
  pasos manuales no registrados.
- Reutilizar schemas, IDs, vocabularios, entidades y pipelines existentes.
- Mantener separadas configuración, ejecución, resultados, validación y
  decisión.
- Diseñar datasets canónicos como frontera entre herramientas: DWSIM no es la
  fuente directa de un dashboard y una vista de Power BI no es la autoridad del
  dato.
- Introducir SQL, APIs, JSON-LD, Knowledge Graph o nuevas capas sólo con un
  caso de uso, contrato, procedencia y prueba definidos.
- Evitar cambios retroactivos de significado. Una corrección crea una nueva
  versión o derivación trazable.

## Evidencia y afirmaciones

No colapsar estos conceptos:

- `evidence_mode`: experimental, calculated, simulated, estimated o
  documentary;
- `data_origin`: empirical, literature, synthetic o hypothetical;
- integridad, convergencia, paridad, validación científica, aptitud industrial
  y decisión.

Un estado guardado de DWSIM no demuestra recálculo. Un mensaje de éxito no
demuestra convergencia verificada. Una réplica del autor no es reproducción
independiente. Un `PASS` de schema o checksum no valida el fenómeno físico.

Toda conclusión debe poder recorrer:

> fuente → transformación → resultado → validación → decisión

Si falta un eslabón, declararlo `NOT_RUN`, `NOT_DEMONSTRATED`, `CONDITIONAL` o
con la limitación equivalente del contrato; nunca rellenarlo con un supuesto
presentado como resultado.

## Flujo mínimo para cambios

1. Inspeccionar el estado de Git, contratos existentes y evidencia afectada.
2. Clasificar el cambio: documentación, fuente, transformación, simulación,
   dataset, validación, visualización o decisión.
3. Definir qué artefacto es autoridad y cuáles son derivados.
4. Implementar el cambio mínimo sobre una rama temática.
5. Actualizar documentación, procedencia y changelog cuando corresponda.
6. Ejecutar las pruebas focalizadas y después los controles integrales
   proporcionales al riesgo.
7. Publicar mediante PR; no fusionar evidencia pendiente como si estuviera
   validada.

Para orientación de proyecto, consultar
[`docs/12_project_direction.md`](docs/12_project_direction.md). Para ejecuciones
DWSIM, consultar [`docs/11_simulation_run_contract.md`](docs/11_simulation_run_contract.md)
y [`docs/adr/0001-dwsim-version-policy.md`](docs/adr/0001-dwsim-version-policy.md).
