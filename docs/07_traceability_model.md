# 07 — Modelo de Trazabilidad

## Componentes

| Componente | Ubicación | Schema |
|---|---|---|
| Metadata del caso | `cases/<NNN>/metadata.yaml` | `schemas/case_metadata.schema.json` |
| Provenance | `cases/<NNN>/provenance.json` | `schemas/provenance.schema.json` |
| Sidecar de dataset | `<dataset>.meta.yaml` | `schemas/dataset.schema.json` |

## `provenance.json` (W3C PROV-lite)

```json
{
  "case_id": "NNN_slug",
  "generated_at": "2026-05-15T12:00:00Z",
  "agents": [
    { "id": "agent:author", "type": "person", "name": "Roberto Flores" }
  ],
  "activities": [
    {
      "id": "act:simulate",
      "started_at": "...",
      "ended_at": "...",
      "software": "DWSIM 8.x",
      "parameters": { "thermo_pkg": "Peng-Robinson" }
    }
  ],
  "entities": [
    {
      "id": "ent:output_table",
      "path": "data/processed/...csv",
      "checksum_sha256": "...",
      "derived_from": ["ent:input_dataset"]
    }
  ]
}
```

## Lineage
- Cada `entity` declara `derived_from` (lista de IDs).
- Cada `activity` declara software, versión y parámetros.
- Cada `entity` final tiene SHA-256 verificable.

## Verificación
`compute_checksums.py --verify` falla si el hash recalculado no coincide
con el declarado.
