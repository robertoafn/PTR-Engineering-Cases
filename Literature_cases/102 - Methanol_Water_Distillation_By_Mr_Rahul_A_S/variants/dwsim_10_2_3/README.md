# Objetivo reproducible DWSIM 10.2.3

Esta ruta reserva la línea `target_reproducible` fijada por la ADR 0001. No
contiene todavía una simulación promovida y no autoriza copiar aquí los estados
RC del workspace externo.

La primera ejecución será `raoult_target/` y deberá incluir:

1. entrada separada derivada del baseline, sin sobrescribirlo;
2. recálculo desde inicio limpio y convergencia verificada;
3. DWSIM 10.2.3 estable, solver y modelo de entalpía explícitos;
4. `SimulationRun`, salida, dataset de resultados, tiempos y hashes;
5. comparación estructural y numérica con el baseline, sin confundirla con
   validación experimental.

NRTL, UNIQUAC y Modified UNIFAC Dortmund usarán rutas y `SimulationRun`
independientes. El benchmark `T-x-y` controlará presión, malla de composición,
parameter set y modelo de entalpía antes de comparar la columna completa.
