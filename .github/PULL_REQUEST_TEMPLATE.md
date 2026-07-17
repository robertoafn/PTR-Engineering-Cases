## Tipo de cambio
- [ ] Nuevo caso
- [ ] Mejora de caso existente
- [ ] Documentación / gobernanza
- [ ] Scripts / automatización
- [ ] Refactor / mantenimiento

## Caso afectado
`<case_id>` (si aplica)

## Objetivo técnico
Describir la pregunta de ingeniería, el fenómeno y el resultado verificable.

## Cambios incluidos
- ...

## Datos y confidencialidad
- [ ] Los datos están clasificados como `synthetic`, `hypothetical`, `simulated`
      o `literature`.
- [ ] No se incluyen datos operacionales internos, propietarios o confidenciales.
- [ ] Las limitaciones y el dominio de validez están documentados.

## Cumplimiento de gobernanza
- [ ] `metadata.yaml` válido contra schema.
- [ ] Datasets y sidecars validados contra `dataset.schema.json`.
- [ ] Columnas CSV vinculadas explícitamente con sus símbolos científicos.
- [ ] Unidades SI verificadas.
- [ ] QC checklist completado.
- [ ] Checksums SHA-256 verificados.
- [ ] Provenance actualizado.
- [ ] Naming conforme.
- [ ] CHANGELOG actualizado en raíz y caso, si aplica.
- [ ] Estado declarado: `draft | review | validated | published`.

## Validación ejecutada
Comando obligatorio:

```bash
python scripts/preflight.py cases/<case_id>
```

Resultado:

```text
<PASS/FAIL y resumen>
```

Para simulaciones DWSIM indicar:

- versión de DWSIM;
- paquete termodinámico y especificaciones relevantes;
- apertura y resolución del archivo versionado;
- balances o cálculos independientes;
- criterios de aceptación y desviaciones;
- si la validación fue del autor o independiente.

## Reproducibilidad
Pasos adicionales para reproducir end-to-end:

1. ...
2. ...

## Evidencia visual
- [ ] Flowsheet, gráfico o tabla ejecutiva añadida, cuando aporte valor.
- [ ] Figuras identificadas y vinculadas desde el README del caso.

## Referencias
DOI, normas, documentación oficial y fuentes abiertas utilizadas.
