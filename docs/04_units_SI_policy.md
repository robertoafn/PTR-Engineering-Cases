# 04 — Política de Unidades (SI)

## Principio
Toda magnitud científica/ingenieril en este repositorio se expresa en
**unidades SI**, salvo excepciones declaradas y justificadas.

## Unidades base
kg, m, s, K, mol, A, cd. (Vocabulario en `schemas/units.controlled_vocabulary.yaml`.)

## Derivadas aceptadas
Pa, J, W, N, Hz, m³, mol/m³, kg/m³, J/(mol·K), W/(m·K), Pa·s, entre otras.

## No-SI tolerados
| Unidad | Condición |
|---|---|
| °C | Convertir a K antes de cálculo; declarar en metadata |
| bar | 1 bar = 1e5 Pa; declarar conversión |
| L   | 1 L = 1e-3 m³ |
| h   | 1 h = 3600 s |

## Prohibidas
`psi`, `atm`, `mmHg`, `cal`, `BTU`, `°F`, `°R`.

## Verificación
`scripts/unit_consistency_check.py` valida `metadata.yaml` y sidecars de
datasets contra el vocabulario controlado. Se ejecuta en CI.

## Referencia
BIPM, *The International System of Units (SI Brochure)*, 9ª ed., 2019.
