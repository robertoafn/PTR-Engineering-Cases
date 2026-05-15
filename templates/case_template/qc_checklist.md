# QC Checklist — <case_id>

- [ ] `metadata.yaml` validado contra `schemas/case_metadata.schema.json`
- [ ] Cada dataset con sidecar `.meta.yaml` válido
- [ ] Unidades SI verificadas (`unit_consistency_check.py` PASS)
- [ ] Sin nulos en campos obligatorios
- [ ] Rangos físicamente plausibles
- [ ] Integridad referencial entre tablas
- [ ] Naming conforme `docs/03_naming_conventions.md`
- [ ] Checksums SHA-256 generados y verificados
- [ ] `provenance.json` completo (agents, activities, entities)
- [ ] Referencias verificadas (DOI/ISBN comprobado)
- [ ] Reproducibilidad end-to-end probada (Restart & Run All)
- [ ] `validation_report.md` con veredicto declarado
- [ ] `CHANGELOG.md` del caso actualizado
- [ ] Status declarado en `metadata.yaml`
