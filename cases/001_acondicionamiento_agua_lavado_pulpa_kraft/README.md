# 001_acondicionamiento_agua_lavado_pulpa_kraft — Acondicionamiento de agua para lavado de pulpa Kraft

> **Status:** review  
> **Versión:** 0.1.0  
> **Aviso de datos:** entradas sintéticas y resultados simulados.  
> **No representa condiciones operacionales reales ni datos internos de CMPC.**

---

## 1. Fenómeno

El caso representa una línea auxiliar de acondicionamiento de agua asociada conceptualmente
al lavado de pulpa Kraft. La corriente se presuriza mediante una bomba y se calienta antes
de ingresar a una operación de lavado.

Los fenómenos principales son:

- transporte de cantidad de movimiento en un líquido prácticamente incompresible;
- conversión de trabajo de eje en incremento de presión y entalpía;
- transferencia de energía sensible en un calentador;
- conservación de masa y energía en estado estacionario.

Escala: industrial-simulada. Régimen: estacionario. Fases consideradas: líquido-vapor,
aunque las tres corrientes resultan completamente líquidas.

## 2. Objetivo

Determinar la potencia de bombeo y la carga térmica necesarias para acondicionar
`10 kg/s` de agua desde `303.15 K` y `300000 Pa` hasta `343.15 K` y `580000 Pa`,
con una presión intermedia de `600000 Pa`.

## 3. Contexto industrial

En el proceso Kraft, la pulpa descargada desde la cocción contiene licor negro residual.
El lavado busca desplazar este licor desde la matriz fibrosa, reducir el arrastre hacia
etapas posteriores y recuperar materia orgánica y químicos hacia el circuito de recuperación.

Este caso no simula el lavador, la suspensión de fibras ni el licor negro. Representa
únicamente un sistema auxiliar simplificado de bombeo y acondicionamiento térmico de agua.
La asociación con CMPC es contextual y didáctica; no se utilizan datos propietarios ni
condiciones de una planta específica.

## 4. Fundamento científico

### 4.1 Balance de masa

En estado estacionario y sin acumulación:

```math
\dot m_{in} = \dot m_{out}
```

### 4.2 Potencia de bombeo

Para agua líquida aproximadamente incompresible:

```math
\dot W_{eje} \approx \frac{\dot V\,\Delta P}{\eta}
```

Con `V_dot = 0.01004278 m³/s`, `DeltaP = 300000 Pa` y `eta = 0.75`,
la estimación independiente es `4.01711 kW`.

### 4.3 Carga térmica

El modelo riguroso usa entalpías:

```math
\dot Q = \dot m\left(h_{out}-h_{in}\right)
```

Como comprobación aproximada:

```math
\dot Q \approx \dot m C_p \Delta T
```

Usando `Cp = 4.18 kJ/(kg·K)` se obtiene `1670.72 kW`, frente a
`1670.50 kW` calculados por DWSIM.

## 5. Modelo de ingeniería

- simulador: DWSIM 9.0.5;
- paquete termodinámico: Steam Tables (IAPWS-IF97);
- equilibrio forzado: VLE;
- algoritmo flash: Nested Loops;
- componente: Water;
- bomba especificada por presión de salida;
- calentador especificado por temperatura de salida;
- caída de presión en calentador: `20000 Pa`.

Topología:

```text
MSTR-001_AGUA_FRIA
        |
        v
P-001_BOMBA_AGUA ---- WSTR-001_POTENCIA_BOMBA
        |
        v
MSTR-002_AGUA_PRESURIZADA
        |
        v
H-001_CALENTADOR_AGUA ---- QSTR-001_CALOR_AGUA
        |
        v
MSTR-003_AGUA_ACONDICIONADA
```

## 6. Supuestos

Ver `assumptions.md`.

## 7. Stack y versiones

| Componente | Versión | Licencia | Propósito |
|---|---:|---|---|
| DWSIM | 9.0.5 | GPL-3.0 | Simulación estacionaria |
| Python | 3.13.5 | PSF | Extracción de resultados y QC |

## 8. Entradas

| Variable | Valor SI |
|---|---:|
| Fluido | Water |
| Fracción másica de agua | 1.000 |
| Caudal másico | 10 kg/s |
| Temperatura de entrada | 303.15 K |
| Presión de entrada | 300000 Pa |
| Presión de descarga de bomba | 600000 Pa |
| Eficiencia de bomba | 0.75 |
| Temperatura de salida del calentador | 343.15 K |
| Caída de presión del calentador | 20000 Pa |

## 9. Procedimiento reproducible

1. Validar metadatos:

   ```bash
   python scripts/validate_metadata.py cases/001_acondicionamiento_agua_lavado_pulpa_kraft
   ```

2. Abrir y resolver:

   ```text
   cases/001_acondicionamiento_agua_lavado_pulpa_kraft/simulations/dwsim/001_acondicionamiento_agua_lavado_pulpa_kraft.dwxmz
   ```

3. Verificar consistencia de unidades:

   ```bash
   python scripts/unit_consistency_check.py
   ```

4. Generar o verificar checksums:

   ```bash
   python scripts/compute_checksums.py cases/001_acondicionamiento_agua_lavado_pulpa_kraft
   python scripts/compute_checksums.py --verify cases/001_acondicionamiento_agua_lavado_pulpa_kraft
   ```

5. Ejecutar pruebas:

   ```bash
   pytest
   ```

## 10. Resultados

| Objeto | T (K) | P (Pa) | m_dot (kg/s) | Resultado energético |
|---|---:|---:|---:|---:|
| MSTR-001_AGUA_FRIA | 303.150000 | 300000 | 10.0 | — |
| P-001_BOMBA_AGUA | — | — | — | 4.017111 kW |
| MSTR-002_AGUA_PRESURIZADA | 303.180665 | 600000 | 10.0 | — |
| H-001_CALENTADOR_AGUA | — | — | — | 1670.500718 kW |
| MSTR-003_AGUA_ACONDICIONADA | 343.150000 | 580000 | 10.0 | — |

Dataset: `data/process_results_v01.csv`.

## 11. Validación y QC

Resultados principales:

- residuo global de masa: `0 kg/s`;
- residuo global de energía: `-7.8875E-06 kW`;
- error relativo del balance energético: `2.69E-07 %`;
- desviación de la potencia de bomba respecto a la estimación hidráulica: prácticamente nula;
- desviación del deber térmico respecto a `m_dot Cp DeltaT`: `0.013 %`;
- fracción de vapor de salida: aproximadamente cero.

Ver `validation_report.md` y `qc_checklist.md`.

## 12. Trazabilidad

Ver `provenance.json`.

SHA-256 del archivo de simulación:

```text
ac292d0375b3e71aacc9d3bf1576d5ab6c4e6eeadd77ec210ce49804cba96605
```

## 13. Limitaciones

- El agua se modela como componente puro.
- No se representa pulpa, licor negro, fibras, sólidos, electrolitos ni compuestos orgánicos.
- No se modelan tuberías, altura geométrica, curva real de bomba ni NPSH del sistema.
- La eficiencia de bomba es una especificación sintética.
- El calentador representa un deber energético, no un intercambiador dimensionado.
- No se consideran ensuciamiento, pérdidas térmicas ambientales ni control dinámico.
- Los valores no deben emplearse para diseño de planta o toma de decisiones operacionales.

## 14. Conclusión técnica

El modelo converge y conserva masa y energía dentro de los criterios establecidos.
Para las condiciones sintéticas definidas, la bomba requiere `4.01711 kW` y el
calentador `1670.50072 kW`. El sistema entrega `10 kg/s` de agua a `343.15 K`
y `580000 Pa`, completamente líquida.

## 15. Referencias

Ver `references.bib`.
