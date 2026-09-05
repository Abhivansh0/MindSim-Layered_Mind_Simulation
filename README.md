# MindSim

> **A layered simulation of a mind — not just a system that answers prompts.**

MindSim is an experimental cognitive architecture that explores how **memory, emotion, personality, neural activation, cognition, and time-dependent internal state** can interact to produce persistent and individualized behaviour.

The system processes stimuli through multiple interacting layers rather than treating each interaction as an isolated `input → model → response` operation.

The project is **biologically inspired, but computationally implemented**. It is not intended to be a literal model of the human brain.

---

## Overview

The current processing pipeline is:

```text
Stimulus
   │
   ▼
┌─────────────────┐
│  Neuron Layer   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Memory Retrieval│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Emotion Layer  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Personality Layer│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Cognition    │
│ + Meta-Cognition│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Memory Storage  │
└────────┬────────┘
         │
         ▼
    Dream Layer
```

Memory intentionally appears twice in the pipeline:

```text
Stimulus
   ↓
Memory Retrieval
   ↓
...
   ↓
Cognition
   ↓
Memory Storage
```

Retrieved memories provide context before emotional processing, while the resulting experience can subsequently become part of the mind's persistent state.

**Detailed overview:**  
→ [`docs/overview.md`](docs/overview.md)

---

## Architecture

MindSim is organized as a collection of interacting cognitive layers operating over a shared `MindState`.

```text
                    ┌─────────────────┐
                    │     Stimulus    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Neuron Layer   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Memory Retrieval│
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Emotion Layer  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │Personality Layer│
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    Cognition    │
                    │  Meta-Cognition │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Memory Storage  │
                    └─────────────────┘
```

### Current Architecture Documentation

| Component | Documentation |
|---|---|
| Pipeline | [`pipeline.md`](docs/current_architecture/pipeline.md) |
| MindState | [`mindstate.md`](docs/current_architecture/mindstate.md) |
| Neuron Layer | [`neuron_layer.md`](docs/current_architecture/neuron_layer.md) |
| Memory Layer | [`memory_layer.md`](docs/current_architecture/memory_layer.md) |
| Emotion Layer | [`emotion_layer.md`](docs/current_architecture/emotion_layer.md) |
| Personality Layer | [`personality_layer.md`](docs/current_architecture/personality_layer.md) |
| Simulation Loops | [`simulation_loops.md`](docs/current_architecture/simulation_loops.md) |
| Time System | [`time_system.md`](docs/current_architecture/time_system.md) |

---

## MindState

`MindState` is the central state container of the simulation.

It represents the current state of the simulated mind and acts as the controlled interface through which the cognitive layers exchange information.

Current state includes concepts such as:

```text
current_stimulus
activation_map
emotion_map
working_memory
```

**Documentation:**  
→ [`docs/current_architecture/mindstate.md`](docs/current_architecture/mindstate.md)

---

## Neuron Layer

The neuron layer converts stimuli into activation patterns and maintains neural state over time.

It currently deals with:

- Stimulus embeddings
- Neuron cluster activation
- Activation decay
- Hebbian learning
- Synaptic strengthening
- Synaptic decay

**Documentation:**  
→ [`docs/current_architecture/neuron_layer.md`](docs/current_architecture/neuron_layer.md)

---

## Memory Layer

Memory is treated as a cognitive process rather than a simple database lookup.

The retrieval process considers the relationship between the current stimulus and previously stored experiences before those memories are passed further into the cognitive pipeline.

The memory system also maintains accessibility over time, allowing frequently or recently recalled memories to behave differently from rarely accessed ones.

Memory is therefore both:

```text
Past Experience
      ↓
Retrieval
      ↓
Current Processing
      ↓
New Experience
      ↓
Future Memory
```

**Documentation:**  
→ [`docs/current_architecture/memory_layer.md`](docs/current_architecture/memory_layer.md)

---

## Emotion Layer

The emotion layer transforms the current activation state into an evolving emotional state.

It includes:

- Base emotions
- Emotion intensity
- Emotional regulation
- Emotional compounding
- Emotional inertia
- Temporal evolution of emotional state

Emotion is therefore not reset after every stimulus. It can persist and influence subsequent processing.

**Documentation:**  
→ [`docs/current_architecture/emotion_layer.md`](docs/current_architecture/emotion_layer.md)

---

## Personality Layer

Personality acts as a modulation mechanism between the generated emotional state and cognition.

The architecture explores how personality descriptors can influence different parts of the system rather than treating personality as a single static prompt.

This includes descriptor-level and descriptor-family effects.

**Documentation:**  
→ [`docs/current_architecture/personality_layer.md`](docs/current_architecture/personality_layer.md)

---

## Cognition

The cognitive layer receives the state produced by the preceding layers and generates the system's response.

Conceptually, cognition has access to:

```text
Stimulus
+ Neural Activation
+ Retrieved Memory
+ Emotional State
+ Personality State
+ Working Memory
```

Meta-cognition provides an additional reasoning layer over the cognitive process.

**Pipeline:**  
→ [`docs/current_architecture/pipeline.md`](docs/current_architecture/pipeline.md)

---

## Simulation

MindSim separates incoming stimulus processing from continuous background evolution.

### Stimulus Loop

```text
Stimulus
   ↓
Neuron
   ↓
Memory Retrieval
   ↓
Emotion
   ↓
Personality
   ↓
Cognition
   ↓
Memory Storage
```

### Background Loop

The internal state continues to evolve independently of incoming stimuli.

This includes processes such as:

```text
Neuron activation decay
Synaptic decay
Emotional inertia
Emotion compounding
State maintenance
```

**Documentation:**  
→ [`docs/current_architecture/simulation_loops.md`](docs/current_architecture/simulation_loops.md)

---

## Time

MindSim operates with two time domains:

```text
Real Time
    │
    ├── Neuron decay
    ├── Refractory timers
    └── Emotional inertia
    │
    ▼
Simulated Time
    │
    ├── Hebbian decay
    └── Long-term processes
```

The separation allows different cognitive processes to operate at different temporal scales.

**Documentation:**  
→ [`docs/current_architecture/time_system.md`](docs/current_architecture/time_system.md)

---

## Design Principles

MindSim is built around several architectural principles.

### Emergent Behaviour

Complex behaviour should emerge from the interaction of simpler mechanisms rather than being explicitly hard-coded.
**Documentation**
→ [`docs/current_architecture/MindSim_Continuity_of_Mind.md`](docs/current_architecture/MindSim_Continuity_of_Mind.md)

### Continuous State

The mind is not reset between stimuli.
Activations, emotions, synaptic weights, and memories persist and evolve over time.

### Biologically-Inspired References

The architecture draws from computational interpretations of:

- Hebbian learning
- Appraisal theory
- OCC emotion model
- Plutchik's emotion framework
- ACT-R-inspired memory mechanisms
- BIG FIVE traits
- Abridged Big 5 Circumplex

These concepts are adapted to the requirements and limitations of a computational simulation.
---

## Architecture Decision Records

The architecture is intentionally documented through ADRs.
Rather than hiding design choices inside implementation details, major architectural decisions are recorded with their motivation, alternatives, and consequences.

### ADRs

- [`ADR-001 — Memory Before Emotion`](docs/ADR/ADR-001-memory-before-emotion.md)
- [`ADR-002 — Per-Cluster Decay Rates`](docs/ADR/ADR-002-per-cluster-decay-rates.md)
- [`ADR-003 — Streak-Based Hebbian Learning`](docs/ADR/ADR-003-streak-based-hebbian.md)
- [`ADR-004 — Emotion Profile Based Mapping`](docs/ADR/ADR-004-emotion-profile-based-mapping.md)
- [`ADR-005 — Manual Semantic Scaling`](docs/ADR/ADR-005-manual-semantic-scaling.md)
- [`ADR-006 — Dual Time System`](docs/ADR/ADR-006-dual-time-system.md)
- [`ADR-007 — Pending Boost Batch Pattern`](docs/ADR/ADR-007-pending-boost-batch-pattern.md)
- [`ADR-008 — Evidence Accumulation for Emotion Mapping`](docs/ADR/ADR-008-evidence-accumulation-emotion-mapping.md)
- [`ADR-010 — Pattern Strength Nudge System`](docs/ADR/ADR-010-pattern-strength-nudge-system.md)
- [`ADR-011 — Descriptor DNA: Static vs Live Activation`](docs/ADR/ADR-011-descriptor-dna-static-vs-live-activation.md)
- [`ADR-012 — Descriptor Family Bias Distribution`](docs/ADR/ADR-012-descriptor-family-bias-distribution.md)
- [`ADR-013 — Emotion-Weighted-Memory-Decay.md`](docs/ADR-013-Emotion-Weighted-Memory-Decay.md)

---

## Experiments

MindSim is developed through iterative experimentation and calibration.
The repository contains experiments covering areas such as:

```text
Neuron behaviour
Memory behaviour
Hebbian learning
Emotion mapping
Descriptor effects
Personality differentiation
Calibration
```

---

## Archived Designs

MindSim has gone through multiple iterations.
Previous approaches are preserved rather than deleted so that architectural evolution can be traced.
Archived documentation includes earlier versions of:

- Pipeline architecture
- Neuron decay
- Hebbian learning
- Emotion mapping

→ [`docs/archived/`](docs/archived/)

---

## Project Structure

```text
MindSim-Layered_Mind_Simulation/
│
├── Brain/
│   ├── Neuron Layer
│   └── Emotion Layer
│
├── Model/
│
├── Simulation/
│
├── config/
│
├── docs/
│   ├── overview.md
│   │
│   ├── current_architecture/
│   │   ├── pipeline.md
│   │   ├── mindstate.md
│   │   ├── neuron_layer.md
│   │   ├── memory_layer.md
│   │   ├── emotion_layer.md
│   │   ├── personality_layer.md
│   │   ├── simulation_loops.md
│   │   └── time_system.md
│   │
│   ├── ADR/
│   │   └── ...
│   │
│   └── archived/
│       └── ...
│
├── Caliberation_Results/
├── memory_db/
├── chroma/
├── chroma_data/
│
├── main.py
└── tests / experiments
```

---

## Status

MindSim is an **active research prototype**.
The architecture is continuously evolving through implementation, experimentation, calibration and architectural revision.
Not every component represents a finished or scientifically validated model.
The project should therefore be understood as:

```text
A computational exploration of cognitive architecture
                    ↓
          not a model of the human brain
```

---

## Documentation Map

If you are new to the project, read in this order:

```text
1. Project Overview
        ↓
2. Current Architecture
        ↓
3. Individual Layer Documentation
        ↓
4. Architecture Decision Records
        ↓
5. Experiments / Calibration
        ↓
6. Source Code
```

### Start Here

→ [`docs/overview.md`](docs/overview.md)

### Architecture

→ [`docs/current_architecture/`](docs/current_architecture/)

### Design Decisions

→ [`docs/ADR/`](docs/ADR/)

### Historical Architecture

→ [`docs/archived/`](docs/archived/)

---

## Philosophy

```text
Traditional AI:

    Input
      ↓
    Model
      ↓
    Response


MindSim:

    Experience
        ↓
    Internal State
        ↓
    Cognitive Processing
        ↓
      Response
        ↓
      Memory
        │
        └──────────────┐
                       ↓
                Future Experience
```

MindSim explores what happens when an AI system is given a **persistent internal state composed of interacting cognitive mechanisms**, rather than treating every interaction as an independent request.

---

## License

See [`LICENSE`](LICENSE).
