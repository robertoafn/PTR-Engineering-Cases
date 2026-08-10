# Dashboard científico PTR

Aplicación local de sólo lectura para **explicar fenómenos científicos y de
ingeniería con la evidencia de los casos**. Los flowsheets y gráficos no son
adornos ni un tablero de aprobaciones: funcionan como apoyo para responder una
pregunta, reconocer un mecanismo, interpretar una ecuación y acotar una
conclusión.

La secuencia de lectura es:

`pregunta → flowsheet → mecanismo → ecuación → datos → interpretación → límites`

Los resultados de validación permanecen disponibles como respaldo auditable,
pero no gobiernan la portada ni sustituyen la explicación física. En v0.6.0 el
dashboard cubre exclusivamente los casos PTR 001–004.

## Ejecutar

Desde la raíz del repositorio:

```bash
streamlit run dashboards/streamlit/app.py
```

En Windows, usando el entorno virtual del repositorio:

```powershell
.\.venv\Scripts\python.exe -m streamlit run dashboards\streamlit\app.py
```

Abra `http://localhost:8501` si el navegador no se inicia automáticamente.

## Recorrido de la interfaz

- **Mapa científico:** presenta la pregunta y los fenómenos de cada caso;
  distingue la continuidad material 002→003 de la continuidad de modelo
  003→004.
- **Estudiar un caso:** sitúa primero el flowsheet y su guía de lectura; después
  desarrolla cada fenómeno con ecuación, datos, interpretación y limitaciones.
- **Conectar fenómenos:** compara preguntas y mecanismos por dominio científico.
- **Rigor y fuentes:** conserva estados, criterios, datasets y procedencia para
  auditoría, en una capa deliberadamente secundaria.

Cada caso utiliza figuras específicas para su pregunta:

- Caso 001: presión, temperatura, potencia hidráulica y carga térmica;
- Caso 002: expansión isoentálpica, reparto de masa y metanol, cromatogramas y
  calibración sintética;
- Caso 003: perfiles térmicos, balance de calor, LMTD y margen hidráulico;
- Caso 004: reparametrización UA, sensibilidad U–caudal, perfiles térmicos,
  orden nominal de presiones y jerarquía de validación cruzada.

El Caso 102 de `Literature_cases/` aún no aparece en la interfaz. Su estado
actual acredita la identidad e integridad del original FOSSEE, no una
reconvergencia ni una validación científica. Se incorporará cuando el usuario
aporte la reproducción DWSIM 9.0.5 y el caso disponga de resultados, figuras y
conclusiones reproducibles. Las variantes con otros paquetes termodinámicos se
compararán por separado y no sustituirán el archivo fuente.

## Fuentes y transformaciones

- `metadata.yaml`: identidad, versión, entradas y ciclo de vida del caso;
- CSV declarados por el caso: estados de proceso y evidencia analítica;
- figuras versionadas: representación del flowsheet o evidencia visual;
- `validation_results.json`: criterios, resultados, alcance y procedencia;
- `case_catalog.yaml`: preguntas, mecanismos, ecuaciones, guía de figuras,
  interpretación y límites;
- `science_model.py`: magnitudes didácticas recalculadas desde los datasets.

El catálogo editorial no reemplaza la evidencia cuantitativa. Las
transformaciones científicas no modifican archivos fuente ni vuelven a resolver
las simulaciones.

## Convenciones rigurosas

- una coincidencia numérica es evidencia computacional, no validación
  experimental;
- `FAIL` de calidad de datos no se presenta como falla del fenómeno físico;
- `CONDITIONAL` identifica una conclusión relevante que la evidencia aún no
  demuestra;
- un margen de presión de `0 Pa` no prueba una barrera hidráulica;
- un margen nominal de `+50 kPa` no demuestra suficiencia, integridad ni
  seguridad durante transitorios o fallas;
- las señales cromatográficas del Caso 002 son sintéticas y sus áreas canónicas
  fueron integradas externamente;
- todas las conclusiones visibles incluyen su dominio de validez.

## Incorporar un caso nuevo

1. publicar `metadata.yaml`, datasets, figura y `validation_results.json`;
2. agregar al catálogo su pregunta, objetivos, guía visual, métodos, fenómenos,
   ecuaciones, interpretación, conclusión y límites;
3. implementar en `science_model.py` sólo las transformaciones necesarias para
   explicar sus datos;
4. crear figuras específicas para sus mecanismos, sin reutilizar gráficos
   genéricos que oculten el significado físico;
5. asociar cada fenómeno con sus criterios mediante `evidence_criteria`;
6. ampliar las pruebas científicas y revisar visualmente la aplicación.

Para `Literature_cases/`, primero se conserva el original inmutable con su
manifiesto, SHA-256, licencia y procedencia, y se ejecuta
`scripts/validate_literature_case.py`. La mera promoción de la fuente no cumple
los requisitos del paso 1: hacen falta resultados propios antes de extender el
catálogo del dashboard.

## Verificar

```bash
pytest tests/test_dashboard_data.py -q
python scripts/preflight.py
```

El dashboard no requiere dependencias adicionales respecto de
`requirements.txt`.
