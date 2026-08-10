# Roadmap v0.6.0 - cierre PTR e inicio de Literature Cases

## Objetivo

Cerrar el alcance de desarrollo de los Casos PTR 001-004 sin alterar sus
veredictos, sincronizar el Caso 004 y redirigir el crecimiento del repositorio
hacia casos existentes del corpus FOSSEE. El primer caso promovido es el 102,
Methanol Water Distillation.

## Resultado del release

| Entregable | Estado | Evidencia |
|---|---|---|
| Casos PTR 001-004 congelados como baseline auditable | Completado | Índice y reportes conservan PASS/FAIL/CONDITIONAL |
| Caso 004 integrado y sincronizado | Completado | DWSIM, datasets, sensibilidad, figuras, sidecars y procedencia |
| Paridad final del Caso 002 | Ejecutada: FAIL | 0.115554596 % en energía frente a 0.05 % |
| Corpus FOSSEE fuera de Git | Completado | Regla anclada en `.gitignore` |
| Literature Case 102 promovido | Completado | 2/2 originales idénticos al corpus |
| Validador de Literature Cases | Completado | Hash, tamaño, rutas y paridad opcional |
| DWSIM 9.0.5 del Caso 102 | Pendiente del usuario | Ruta reservada en `variants/` |
| Comparación NRTL/VLE | No ejecutada | Requiere variante y fuentes trazables |

## Contrato de cierre de los Casos 001-004

El cierre es de alcance, no una promoción automática:

| Caso | Ciclo de vida | Veredicto publicado | Tratamiento |
|---|---|---|---|
| 001 | `validated` | `PASS` | Cerrado |
| 002 | `review` | `FAIL` | Cerrado con deuda energética explícita |
| 003 | `review` | `CONDITIONAL` | Cerrado con margen hidráulico no demostrado |
| 004 | `review` | `CONDITIONAL` | Cerrado con fase y validaciones externas abiertas |

Los Casos 002-004 sólo se reabren ante nueva evidencia o para corregir un
defecto documentado. No se convierten en `validated` por decisión editorial.

## Arquitectura Literature Cases

`corpus local ignorado → selección → copia inmutable → manifiesto y licencia →
paridad de versión → variantes separadas → comparación científica`

El corpus completo permanece en
`references/Literature_cases_references/`. Su existencia local no implica que
todo caso pueda ni deba publicarse. `Literature_cases/` contiene únicamente
los casos trabajados y promovidos.

## Caso 102

La ficha oficial atribuye Methanol Water Distillation a Rahul A S, SASTRA
Deemed University, 2018, y declara DWSIM v6.5 Classic UI. El XML del archivo
contiene build 5.5.6886.34470. Ambos datos se conservan como evidencia
discordante. El baseline usa Raoult's Law y no se modifica.

La siguiente secuencia es obligatoria:

1. el usuario crea una copia en DWSIM 9.0.5 conservando Raoult;
2. se compara topología, especificaciones, balances, purezas, temperaturas,
   perfiles y deberes térmicos;
3. sólo después se crea una variante NRTL u otra opción justificada;
4. la comparación termodinámica se contrasta con VLE trazable.

## Criterio de cierre v0.6.0

- [x] corpus FOSSEE ignorado y no rastreado;
- [x] sólo el Caso 102 promovido en `Literature_cases/`;
- [x] originales 102 sin cambios y con SHA-256;
- [x] discrepancias de versión y autoría documentadas;
- [x] Caso 004 y documentación sincronizados;
- [x] estados 001-004 honestos;
- [x] versión, changelog, citación, pruebas y enlaces sincronizados;
- [ ] paridad DWSIM 9.0.5 del Caso 102, fuera del alcance porque el archivo aún
  no ha sido entregado por el usuario.

El próximo ciclo se orienta a la paridad y comparación científica del Caso 102,
no a crear un nuevo caso PTR desde cero.
