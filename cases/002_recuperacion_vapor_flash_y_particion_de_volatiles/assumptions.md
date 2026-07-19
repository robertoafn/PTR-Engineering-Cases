# Supuestos — Caso 002

## Modelo de proceso

- Operación en estado estacionario.
- La alimentación es una mezcla sintética binaria de agua y metanol.
- La composición de entrada se fija en fracción másica: `w_H2O = 0.999` y `w_MeOH = 0.001`.
- La válvula `V-201` es adiabática, sin trabajo de eje y se especifica por presión de salida.
- `SEP-201` separa las fases resultantes sin caída de presión ni deber térmico adicional.
- NRTL es el paquete principal para representar la no idealidad líquida de agua-metanol. Los parámetros binarios provienen de la base interna de DWSIM y no se validan experimentalmente en este caso.

## Muestreo y cromatografía

- `OC-MSTR-203` representa una muestra de vapor flash condensado totalmente antes de su análisis, no una inyección directa de una fase gaseosa.
- Los cromatogramas GC-FID son sintéticos y se generan con ruido controlado, un único pico de metanol y una línea base no plana.
- Los estándares cubren 0.10 a 1.00 kg/m³ en vial.
- Las áreas de pico se reconstruyen por regla trapezoidal externa con corrección de línea base local; esta decisión se debe a que la integración interna de OpenChrom 1.6.14 devolvió área `0.0` para el archivo FID importado.
- El resultado externo se etiqueta explícitamente como `external_reconstruction_from_OpenChrom_xy`.

## Interpretación

- El caso evalúa coherencia de flujo y trazabilidad entre simulación y datos sintéticos, no validación experimental independiente del equilibrio vapor-líquido.
- Una concentración cromatográfica se considera una concentración de vial; cuando aplica, el factor de dilución se conserva en el dataset canónico.
- No se infieren límites ambientales, criterios de descarga ni aptitud operacional real a partir del metanol sintético.
