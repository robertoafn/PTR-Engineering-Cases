# QC Checklist — 004_control_contaminacion_cruzada_validacion_cruzada

## Evidencia disponible

- [x] Archivo DWSIM entregado por el autor y renombrado conforme al `case_id`.
- [x] SHA-256 de la simulación verificado:
  `e62493025e33114466e1af735c5916eb73eaa92d36ea6d2419e456875d0a181e`.
- [x] DWSIM 9.0.5 Automation API resolvió una copia temporal.
- [x] Cinco objetos requeridos extraídos mediante API.
- [x] Archivo fuente confirmado sin cambios durante la ejecución.
- [x] U, A, F, dirección de flujo y caídas internas documentados.
- [x] Modelo identificado como UA sin rating geométrico detallado.
- [x] Advertencia de cambio de fase y pequeña fracción vapor documentadas.
- [x] Reparametrización circular de UA documentada.
- [x] Brecha de validación calorimétrica documentada.
- [x] Margen nominal de +50000 Pa separado de una afirmación de seguridad.
- [x] Figuras nominal y de sensibilidad derivadas de CSV versionados.
- [x] Scripts con salidas atómicas y rechazo de colisiones entrada↔salida.
- [x] Fracciones molar y másica de vapor extraídas de forma reproducible.
- [x] `status: review` declarado en `metadata.yaml`.
- [x] `validation_results.json` generado por el motor, no editado manualmente.

## Gobernanza pendiente de ejecución final

- [x] `metadata.yaml` validado contra `schemas/case_metadata.schema.json`.
- [x] `validation_spec.yaml` validado contra su schema.
- [x] Dataset canónico `data/process_results_v01.csv` generado.
- [x] Sidecars de los tres datasets completos y válidos.
- [x] Unidades verificadas con el vocabulario controlado.
- [x] Rangos, tipos y nulos revisados.
- [ ] Naming global conforme.
- [ ] Checksums de todos los artefactos técnicos declarados actualizados.
- [x] `provenance.json` validado contra su schema.
- [ ] Preflight integral aprobado.

## Validación científica pendiente

- [x] Balance de masa nominal reconstruido por ambos lados.
- [x] Balance de energía nominal reconstruido.
- [x] Réplica de LMTD dentro de 0.1 K.
- [x] Margen de presión nominal mayor que cero.
- [ ] Hipótesis monofásica estricta demostrada.
- [x] Sensibilidad de U y caudal frío ejecutada y versionada (12/12).
- [ ] Referencia DECHEMA exacta y licencia resueltas.
- [ ] Parámetros y coeficientes NRTL comparados sin mezclar convenciones.
- [ ] Datos VLE experimentales trazables incorporados.
- [ ] Comparación VLE reproducible completada.
- [ ] Evidencia calorimétrica o de propiedades independiente incorporada.
- [ ] Paridad energética del Caso 002 resuelta en su propio caso.
- [x] `validation_results.json` generado por el motor declarativo.
- [ ] Resultado estructurado sin criterios requeridos pendientes.

## Ciclo de vida

- [x] Caso 004 conservado en `review`.
- [x] Caso 002 no promovido.
- [x] Caso 003 no promovido ni reescrito.
- [ ] Criterios de cierre satisfechos para promover 004 a `validated`.
