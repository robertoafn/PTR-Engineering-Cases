# Changelog - Literature Case 102

## Unreleased

- DWSIM 9.0.5 se reclasifica como reproducción histórica opcional y no
  bloqueante; la línea reproducible sigue la versión estable de ADR 0001.
- El siguiente gate pasa a ser el dataset VLE experimental gobernado y el
  recálculo limpio, seguidos por el benchmark de cuatro modelos.
- Se reserva `variants/dwsim_10_2_3/` como línea `target_reproducible`, sin
  incorporar aún una simulación.
- Las réplicas 10.2.0 del autor y la extracción preliminar de Álvarez et al. se
  reconocen como contexto local no promovido, sin cambiar el veredicto
  `SOURCE_BASELINE_VERIFIED`.

## 0.2.0 - 2026-08-26

- Se añadió el primer `SimulationRun` canónico para la inspección de sólo
  lectura del baseline FOSSEE ya versionado.
- Se separó explícitamente inspección, recálculo, convergencia y validación
  científica.
- Se alineó la secuencia de trabajo con la política de versiones DWSIM y la
  futura comparación VLE experimental.

## 0.1.0 - 2026-08-09

- Se promovieron `Abstracts.pdf` y `MethanolDistillation.dwxmz` sin
  modificaciones desde el corpus FOSSEE local.
- Se registraron tamaños, SHA-256, atribución y licencia.
- Se documentó la discrepancia entre DWSIM v6.5 declarado y build 5.5.6886
  embebido.
- Se inspeccionó el estado guardado sin reconvergencia.
- Se reservó una ruta separada para la futura variante DWSIM 9.0.5 del usuario.
