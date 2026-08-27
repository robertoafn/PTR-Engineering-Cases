# Variante histórica DWSIM 9.0.5 — opcional

Esta carpeta no contiene todavía una simulación. Se conserva para el compromiso
histórico `reference_reproduction` de v0.6.0; no bloquea el objetivo
`target_reproducible` definido por la ADR 0001. El baseline FOSSEE ubicado en la
raíz del caso es inmutable.

Si se ejecuta esta reproducción:

1. `parity_raoult/`: copia abierta, guardada y resuelta con DWSIM 9.0.5 sin
   cambiar deliberadamente especificaciones ni paquete;
2. se registra con su propio `SimulationRun`, resultados y hashes;
3. no se usa como contenedor de las ejecuciones estables ni de modelos
   alternativos.

Cada archivo nuevo debe tener nombre inequívoco, checksum, metadata, resultados
exportados y un informe que compare contra el baseline.
