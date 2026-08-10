# Changelog — 004_control_contaminacion_cruzada_validacion_cruzada

Formato: [Keep a Changelog 1.1](https://keepachangelog.com/en/1.1.0/) · SemVer.

## [Unreleased]

### Pending

- Comparaciones NRTL-DECHEMA y VLE-literatura.
- Paridad final del Caso 002.
- Figura VLE, condicionada a datos experimentales trazables.

## [0.1.0] - 2026-08-02

### Added

- Simulación manual DWSIM 9.0.5 de HX-301 con NRTL, modo UA,
  `U = 1000 W/(m²·K)`, `A = 13 m²` y `F = 1`.
- Presión de entrada del lado limpio de 350000 Pa frente a 300000 Pa en el
  lado contaminado.
- Documentación canónica, especificación declarativa y trazabilidad SHA-256.
- Resultados nominales verificados mediante Automation API.
- Dataset canónico de corrientes, dataset del equipo y sidecars con checksum.
- Fracciones molar y másica de vapor extraídas desde el estado guardado.
- Malla Automation3 de 12 escenarios para U y caudal frío.
- PFD conceptual instrumentado y figura de sensibilidad generados por script.
- Figuras derivadas de CSV versionados, con validación de malla, margen de
  presión y colisiones de rutas.
- Lectura reproducible del estado guardado sin modificar el archivo DWSIM.
- Resultado estructurado `CONDITIONAL` generado por el motor declarativo.

### Documented

- Advertencia persistida de cambio de fase en el lado caliente.
- Ausencia de rating geométrico detallado.
- Circularidad de la reparametrización UA.
- Brecha calorimétrica independiente.
- Referencias DECHEMA, U y VLE aún no resueltas.
- Separación entre margen hidráulico nominal y seguridad operacional.

### Changed

- Scripts de extracción, sensibilidad, paridad, NRTL, VLE y figuras endurecidos
  contra colisiones entre entradas y salidas.
- Nombres de salida NRTL/VLE y tolerancia térmica VLE alineados con
  `validation_spec.yaml`.

### Notes

- Estado inicial: `review`.
- Veredicto esperado: `CONDITIONAL`.
- Los casos 002 y 003 no se promueven ni se modifican como consecuencia de
  este punto nominal.
