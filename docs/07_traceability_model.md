# 07 — Modelo de Trazabilidad

## Componentes

| Componente | Ubicación | Schema |
|---|---|---|
| Metadata del caso | `cases/<NNN>/metadata.yaml` | `schemas/case_metadata.schema.json` |
| Provenance | `cases/<NNN>/provenance.json` | `schemas/provenance.schema.json` |
| Sidecar de dataset | `<dataset>.meta.yaml` | `schemas/dataset.schema.json` |
| Ejecución de simulación | `<case>/runs/<run_id>/simulation_run.json` | `schemas/simulation_run.schema.json` |

## `SimulationRun`

Cada registro relaciona una actividad de simulación con sus agentes,
configuración termodinámica y artefactos inmutables. Distingue una inspección
de estado guardado de un recálculo y mantiene separados convergencia, paridad
y validación científica. Contrato completo:
[docs/11_simulation_run_contract.md](11_simulation_run_contract.md).

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
      "path": "data/process_results_v01.csv",
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
con el declarado. Acepta tanto el contenedor completo como un caso individual:

```bash
python scripts/compute_checksums.py --verify cases/
python scripts/compute_checksums.py --verify cases/003_slug/
```
