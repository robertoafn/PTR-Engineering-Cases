# Periodic Table Research — From Elements to Industrial Decisions

## Ecosistema interoperable de casos científicos e industriales de ingeniería química

**Periodic Table Research (PTR)** es un marco abierto y reproducible para transformar fenómenos físico-químicos, evidencia científica, modelos y simulaciones en **casos de ingeniería trazables que progresan desde la comprensión fundamental hasta la decisión industrial**.

PTR no se organiza como una colección aislada de simulaciones, datasets o dashboards. Cada caso constituye una implementación **End-to-End** que aporta conocimiento reutilizable a una arquitectura común:

**elementos → sustancias → estructura y propiedades → interacciones → fenómenos → modelos → evidencia → simulación → validación → proceso → energía → ambiente → economía → operaciones → supply chain → decisión → control**

El objetivo es construir progresivamente un ecosistema donde nuevos casos puedan **reutilizar entidades, datos, evidencia, modelos, métodos, estándares y decisiones de casos anteriores**, evitando silos y aumentando el valor acumulativo del repositorio.

---

## Caso fundacional — PTR Case 102

El **Case 102 — Methanol–Water Distillation**, derivado de un caso FOSSEE/DWSIM, constituye la primera implementación fundacional del nuevo modelo PTR.

El caso utiliza el sistema **Methanol–Water** para desarrollar y validar progresivamente la arquitectura completa:

**composición molecular y propiedades
→ equilibrio vapor–líquido
→ modelos termodinámicos
→ simulación DWSIM
→ evidencia experimental independiente
→ comparación y validación de modelos
→ balances de masa y energía
→ sensibilidad e incertidumbre
→ impacto energético y ambiental
→ CAPEX/GHG cuando exista evidencia suficiente
→ alternativas y trade-offs
→ decisión industrial**

La comparación entre **Raoult's Law, NRTL, UNIQUAC y Modified UNIFAC (Dortmund)** permite establecer el primer patrón reproducible para distinguir:

* evidencia experimental;
* cálculos y correlaciones;
* resultados simulados;
* estimaciones;
* hipótesis;
* decisiones derivadas.

Case 102 no representa una plantilla rígida que todos los casos deban replicar completamente. Representa el **primer Digital Thread científico-industrial de referencia** desde el cual nuevos casos pueden adoptar únicamente las capas que correspondan a su dominio.

---

## Marco PTR End-to-End

Cada caso puede evolucionar mediante capas interoperables:

### 1. Scientific Foundation

**Element → Substance → Structure → Property → Interaction → Phenomenon**

Identificación química, propiedades físico-químicas, mecanismos moleculares y fenómenos relevantes.

### 2. Evidence & Models

**Evidence → Assumption → Hypothesis → Model → Parameter**

Literatura primaria, datasets experimentales, ecuaciones, modelos constitutivos, parámetros y límites de aplicabilidad.

### 3. Computational Engineering

**Model → SimulationRun → Result → Sensitivity → Validation**

DWSIM funciona como laboratorio computacional principal para simulación de procesos. Python, SQL y otras herramientas se incorporan cuando mejoran extracción, transformación, comparación, optimización o reproducibilidad.

### 4. Process & Industrial Context

**Unit Operation → Process → Energy → Safety → Environment → Economics**

Los resultados científicos se proyectan progresivamente hacia desempeño de proceso, consumo energético, seguridad, emisiones, CAPEX/OPEX y otras variables industriales cuando el caso disponga de evidencia suficiente.

### 5. Operations & Value Chain

**Plant → Logistics → Supply Chain → Customer → Scenario**

Los casos que lo requieran pueden extenderse hacia producción, inventario, transporte, servicio, demanda, clientes y cadena de suministro.

### 6. Industrial Decision

**Evidence → Alternatives → Constraints → Uncertainty → Trade-off → Decision → Control**

El objetivo final no es producir un resultado numérico aislado, sino documentar **qué evidencia sustenta una decisión, bajo qué supuestos, restricciones e incertidumbre**.

---

## Arquitectura interoperable

PTR utiliza una fuente canónica gobernada desde la cual se generan diferentes proyecciones:

```text
Scientific / Industrial Sources
            │
            ▼
      Deterministic ETL
            │
            ▼
   Canonical Governed Data
            │
     ┌──────┼───────────────┐
     ▼      ▼               ▼
   SQL    Knowledge       Metadata /
 DuckDB     Graph         Provenance
     │      │               │
     └──────┴───────┬───────┘
                    ▼
             Analytical Views
        ┌───────────┼───────────┐
        ▼           ▼           ▼
     Power BI    Obsidian    Reports
```

**Power BI, Obsidian y otras interfaces son proyecciones del conocimiento; no constituyen la fuente canónica.**

La arquitectura busca permitir que cada caso pueda proyectarse simultáneamente como:

* documentación técnica;
* dataset gobernado;
* modelo relacional;
* Knowledge Graph;
* simulación reproducible;
* análisis estadístico;
* modelo Power BI;
* evidencia para una decisión.

---

## Principios del proyecto

PTR prioriza:

**Reproducibilidad**
Un resultado debe poder reconstruirse a partir de sus fuentes, parámetros, software y transformaciones.

**Trazabilidad**
Cada artefacto debe mantener relaciones explícitas con su origen y sus derivados.

**Validación independiente**
Una simulación no valida otra simulación. Cuando corresponda, los modelos deben contrastarse contra evidencia experimental, metrológica o documental independiente.

**Interoperabilidad**
Entidades y relaciones deben poder reutilizarse entre casos, repositorios y herramientas.

**Semántica común**
Sustancias, propiedades, modelos, observaciones, corridas, evidencia y decisiones deben utilizar identificadores y estructuras consistentes.

**Separación epistemológica**
Los datos deben distinguir explícitamente entre:

`experimental · calculated · simulated · estimated · documentary · synthetic · hypothetical`

**FAIR · SI · IUPAC · QC · Provenance**
Los datos y modelos deben permanecer encontrables, accesibles cuando sea posible, interoperables, reutilizables y técnicamente auditables.

---

## Ecosistema acumulativo

Cada nuevo caso debe aportar conocimiento reutilizable.

```text
Case 102
   │
   ├── Methanol
   ├── Water
   ├── VLE
   ├── Raoult
   ├── NRTL
   ├── UNIQUAC
   ├── UNIFAC
   ├── Distillation
   └── Experimental Evidence
          │
          ▼
     Shared PTR Knowledge
          │
     ┌────┼────┬────┐
     ▼    ▼    ▼    ▼
 Case A Case B Case C ...
```

Un compuesto, propiedad, modelo, fuente experimental o método validado en un caso no debería investigarse y modelarse nuevamente desde cero cuando pueda ser reutilizado con provenance explícito.

De esta forma:

> **cada caso amplía el Knowledge Graph y cada nuevo caso puede comenzar desde un nivel de conocimiento superior al anterior.**

---

## Alcance

PTR puede integrar, según la naturaleza de cada caso:

* termodinámica;
* fenómenos de transporte;
* equilibrio de fases;
* operaciones unitarias;
* ingeniería de reacciones;
* simulación de procesos;
* caracterización físico-química;
* metrología y QA/QC;
* análisis estadístico;
* optimización;
* análisis energético;
* seguridad de procesos;
* CAPEX/OPEX;
* emisiones GHG;
* logística;
* supply chain;
* análisis comercial;
* decisiones industriales.

No todas las capas son obligatorias.

La profundidad de un caso está determinada por la **pregunta de ingeniería, disponibilidad de evidencia y decisión que debe soportar**.

---

## Visión

**Periodic Table Research — From Elements to Industrial Decisions** busca convertir casos individuales de ingeniería química en una infraestructura creciente de conocimiento científico-industrial.

El resultado esperado no es solamente un repositorio de ejemplos.

Es una arquitectura capaz de conservar la cadena:

> **qué conocemos → de dónde proviene → cómo fue modelado → cómo fue probado → qué incertidumbre permanece → qué alternativas existen → por qué se tomó una decisión.**

---

## Autor

**Roberto Andrés Flores Núñez**
Ingeniero en Química Industrial — INACAP

**Periodic Table Research — From Elements to Industrial Decisions**

Correo: `roberto.flores.n1987@gmail.com`
Teléfono: `+56 9 7903 8910`
