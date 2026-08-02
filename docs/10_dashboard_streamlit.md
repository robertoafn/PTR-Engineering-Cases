# Protocolo del dashboard científico Streamlit

## Objetivo

La interfaz v0.5.0 convierte artefactos reproducibles del repositorio en una
explicación científica progresiva:

`pregunta → figura → mecanismo → ecuación → dato → interpretación → límite`

El objetivo principal es comprender qué ocurre y por qué ocurre. La validación
cuantitativa demuestra trazabilidad y consistencia dentro del alcance declarado,
pero no es la narrativa principal ni equivale por sí sola a corroboración
experimental, diseño de detalle o demostración de seguridad.

## Arquitectura de información

La aplicación mantiene cuatro capas explícitas:

1. **Evidencia versionada:** metadatos, datasets CSV, resultados JSON y figuras
   de cada caso.
2. **Transformación didáctica:** `science_model.py` deriva magnitudes útiles
   directamente desde los CSV, sin escribir en los casos.
3. **Modelo editorial:** `case_catalog.yaml` declara preguntas, mecanismos,
   ecuaciones, variables, guía de lectura, conclusiones y límites.
4. **Presentación:** `app.py` selecciona una figura adecuada para cada fenómeno
   y deja los controles de validación en `Rigor y fuentes`.

La app descubre únicamente directorios `cases/[0-9][0-9][0-9]_*` con
`metadata.yaml` y `validation_results.json`. `cases/000_template` y las
propuestas documentales no forman parte del portafolio implementado.

## Contrato de explicación por fenómeno

Cada sección científica debe responder, en este orden:

1. ¿Cuál es la pregunta observable?
2. ¿Qué mecanismo físico o químico la explica?
3. ¿Qué ecuación simplificada conecta las variables?
4. ¿Cómo se lee la figura y qué datos la sostienen?
5. ¿Qué significa el resultado para ingeniería?
6. ¿Qué no puede concluirse con esta evidencia?

La figura debe aparecer cerca de la pregunta que responde, con unidades,
caption y una guía de lectura. No se utilizan gráficos genéricos sólo para
mostrar que existen datos.

## Tratamiento por caso

### Caso 001 — trabajo mecánico y calor

Se separan visualmente el aumento de presión producido por P-001 y el aumento
de temperatura producido por H-001. La potencia hidráulica, la potencia de la
bomba y la carga térmica permiten comparar escalas energéticas; la constancia
de 10 kg/s sostiene el balance estacionario.

### Caso 002 — flash, partición y medición

La caída de presión y la invariancia aproximada de entalpía explican la
vaporización parcial. El reparto total de masa se compara con la recuperación de
metanol para mostrar el enriquecimiento del vapor. Los cromatogramas, la curva
de calibración y el RPD de áreas explican la cadena analítica, identificada
explícitamente como sintética y no experimental.

### Caso 003 — transferencia de calor y barrera hidráulica

Los estados térmicos, las cargas de ambos lados y la LMTD explican la
recuperación de calor. La presión se trata como una pregunta distinta: presiones
iguales producen un margen de `0 Pa`, por lo que el caso no demuestra dirección
hidráulica protectora ni integridad del equipo.

### Caso 004 — pregunta metrológica

Mientras sea una propuesta, sólo se presenta la pregunta sobre incertidumbre
GUM/Monte Carlo en HX-301. No se generan distribuciones, intervalos ni
probabilidades sin presupuesto de incertidumbre, correlaciones, código y datos
reproducibles.

## Reglas visuales y de accesibilidad

- texto oscuro sobre fondos claros; no se declara texto blanco;
- unidades visibles y escalas honestas;
- color acompañado de etiquetas y texto, nunca como único canal semántico;
- caption y bloque `Cómo leer la figura` para los flowsheets;
- conclusiones separadas de limitaciones;
- datos y criterios completos disponibles para auditoría;
- estados `FAIL`, `NOT_RUN` y `NOT_DEMONSTRATED` nunca se ocultan.

## Extensión a nuevos casos

1. implementar el caso con la plantilla del repositorio;
2. publicar evidencia estructurada y rutas relativas;
3. definir la pregunta y los objetivos de aprendizaje;
4. documentar mecanismos, ecuaciones, variables e interpretación;
5. agregar transformaciones científicas puras y figuras específicas;
6. vincular cada fenómeno con criterios existentes;
7. probar cálculos, navegación, advertencias y legibilidad visual.

## Ejecución y QA

```bash
streamlit run dashboards/streamlit/app.py
pytest tests/test_dashboard_data.py -q
python scripts/preflight.py
```

La recalculación DWSIM y la regeneración de evidencia continúan bajo
`scripts/validate_case.py` y `docs/09_validation_protocol.md`.
