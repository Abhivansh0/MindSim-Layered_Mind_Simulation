# MindSim — Personality Layer

## Responsibility

The personality layer maintains the agent's evolving OCEAN personality state. It adapts personality from repeated emotional patterns, derives active AB5C descriptors, and applies their associated biases to influence downstream emotional, cognitive, and persistence behavior.

The personality layer contains two deliberately distinct directions of causality:

- **Formation** — emotions build personality over time through repeated memory-linked emotional patterns.
- **Expression** — the current personality state influences live emotional appraisal and downstream behavior.

Formation is slow and bottom-up; expression is fast and top-down.

---

## Processing Pipeline

1. Receive the current emotional pattern associated with the memory/signature node.
2. Map the active emotions to each OCEAN trait using `BIG_FIVE_EMOTION_MAP`, including emotion-intensity zone conditioning.
3. Calculate the net trait vote `P` from the active emotion roles and intensity weights.
4. Calculate pattern strength `G(M)` from the number of memories linked to the same signature node.
5. Calculate `ΔG = G(M_new) - G(M_old)` for the current event.
6. Calculate the personality nudge using `nudge = P × ΔG`.
7. Apply the signed nudge to the OCEAN vector using boundary-safe absorption.
8. Calculate the live activation of all AB5C descriptors from the updated OCEAN vector.
9. Select the descriptor's top-2/threshold hybrid traits using the existing `get_selected_traits` logic.
10. Calculate responsibility distribution across emotional, persistence, and response channels for each descriptor.
11. Classify descriptors into functional families using margin-based dominance with a margin of `0.15`.
12. Generate static emotional DNA for each descriptor from its selected OCEAN poles and emotional-bias templates.
13. Multiply live descriptor activation by static descriptor DNA to calculate the Personality → Emotion influence.
14. Apply the resulting emotional influence to the live emotional appraisal/state.
15. Route persistence and response biases to their respective downstream mechanisms when those mechanisms are implemented.

---

# Part A — Formation

## Emotion → Trait Role Mapping

The formation mechanism uses `BIG_FIVE_EMOTION_MAP` to determine how each of the eight base emotions contributes to each OCEAN trait.

For every trait, an emotion may act as:

- `core` — a primary defining association.
- `supporting` — contributes positively to the trait.
- `contradicting` — contributes negatively to the trait.

The role may also depend on the emotion's intensity zone:

```text
VERY_LOW
LOW
MEDIUM
HIGH
```

Therefore, the same emotion can contribute differently at different intensities.

**Example:**

Fear can act as supporting evidence for Conscientiousness at `MEDIUM` intensity, where moderate arousal can support performance, while acting as contradicting evidence at `LOW` or `HIGH` intensity, where under-stimulation or overwhelming arousal can reduce performance.

> The role mapping is an engineered simulation model informed by psychological relationships. It is not intended to reproduce a clinical or psychometric scoring system.

---

## Net Vote

For one OCEAN trait and one emotional pattern, the personality layer calculates the direction and quality of the trait evidence.

```text
P = Σ(R_i × W_i) / Σ|R_i × W_i|
```

where:

- `R_i` = role weight for the emotion (`core`, `supporting`, or `contradicting`).
- `W_i` = intensity weight associated with the emotion's zone.

The resulting value is bounded to:

```text
[-1, 1]
```

Positive values push the trait toward its positive pole; negative values push it toward its negative pole.

---

## Pattern Strength

Repeated memories linked to the same signature node progressively increase the influence of that pattern.

```text
G(M) = 1 - e^(-(K × M)^n)
```

where:

- `M` = number of memories linked to the signature node.
- `K = 0.01`
- `n = 2`

`K` and `n` are currently **placeholders and are not empirically grounded**.

The curve follows a stretched-exponential / Weibull-CDF-like shape:

- Slow growth at the beginning.
- Steeper growth through the middle.
- Flattening near the ceiling.

`G(M)` is recomputed fully from scratch whenever a memory touches the node. The system does not maintain only an incremental pattern-strength value.

This preserves the intended compounding / sensitization behavior of repeated patterns.

---

## Marginal Pattern Contribution

Only the change in pattern strength produced by the current event is applied:

```text
ΔG = G(M_new) − G(M_old)
```

This prevents the complete historical strength of a pattern from being reapplied every time the pattern is encountered.

Because the growth curve is an S-shaped monotonic function:

- Early memories produce small marginal nudges.
- Middle memories produce the largest marginal nudges.
- Late memories produce progressively smaller nudges as the curve approaches its ceiling.

The resulting marginal effect naturally forms a bell-shaped contribution across repeated reinforcement.

---

## Personality Nudge

The personality nudge for a trait is:

```text
nudge = P × ΔG
```

The sign of `P` determines the direction of personality movement, while `ΔG` determines how much new reinforcement the current event contributes.

A positive nudge moves the trait toward its positive pole.

A negative nudge moves the trait toward its negative pole.

---

## Boundary-Safe OCEAN Update

OCEAN traits are represented continuously in the range:

```text
[-1, 1]
```

The update is asymmetric according to the direction of the nudge.

For a positive nudge:

```text
trait_new = trait_old + nudge × (1 - trait_old)
```

For a negative nudge:

```text
trait_new = trait_old + nudge × (1 + trait_old)
```

This measures the remaining distance toward the boundary in the direction of movement.

The mechanism:

- Prevents a trait from exceeding `[-1, 1]`.
- Produces diminishing movement as the trait approaches either boundary.
- Allows multiple independent patterns to influence the same trait safely.

---

## OCEAN Personality State

The personality state consists of five continuously varying traits:

| Trait | Description |
|---|---|
| `Openness` | Tendency toward novelty, imagination, curiosity, and abstract exploration |
| `Conscientiousness` | Tendency toward organization, discipline, reliability, and goal-directed behavior |
| `Extraversion` | Tendency toward sociability, assertiveness, positive engagement, and outward activity |
| `Agreeableness` | Tendency toward cooperation, empathy, warmth, and interpersonal harmony |
| `Neuroticism` | Tendency toward emotional sensitivity, threat reactivity, and negative-affect susceptibility |

The initial personality state is:

```text
O = 0
C = 0
E = 0
A = 0
N = 0
```

Every trait remains bounded to:

```text
[-1, 1]
```

---

# Part B — Expression

Formation and expression are deliberately separated.

A trait can be built by a particular emotional pattern during formation while having no corresponding tendency to distort that same emotion's appraisal during expression.

**Formation ≠ Expression.**

Formation determines **what personality becomes**.

Expression determines **how the current personality affects live processing**.

---

## Responsibility Distribution

Each OCEAN trait distributes its downstream influence across three channels:

- `emotional_bias` — distorts in-the-moment emotional appraisal.
- `persistence_bias` — makes emotions linger through emotional rumination / lingering.
- `response_bias` — shapes behavioral or action output.

The current static distribution is:

```python
RESPONSIBILITY_DISTRIBUTION = {
    "openness":          {"emotional_bias": 0.4, "persistence_bias": 0.0, "response_bias": 0.6},
    "conscientiousness": {"emotional_bias": 0.0, "persistence_bias": 0.0, "response_bias": 1.0},
    "extraversion":     {"emotional_bias": 0.6, "persistence_bias": 0.0, "response_bias": 0.4},
    "agreeableness":    {"emotional_bias": 0.3, "persistence_bias": 0.0, "response_bias": 0.7},
    "neuroticism":      {"emotional_bias": 0.4, "persistence_bias": 0.5, "response_bias": 0.1}
}
```

Conscientiousness is structurally excluded from emotional and persistence influence:

```text
emotional_bias = 0.0
persistence_bias = 0.0
response_bias = 1.0
```

This is deliberate rather than an omission.

---

## Descriptor Family Bias

Each AB5C descriptor receives a distribution across the three responsibility channels.

The selected traits are determined using the descriptor's existing top-2/threshold hybrid selection logic.

The family bias for a channel is:

```text
family[channel] =
Σ(|selected_trait_value| × RESPONSIBILITY_DISTRIBUTION[trait][channel])
/
Σ|selected_trait_value|
```

The absolute trait value is used deliberately.

The sign of the OCEAN trait is discarded at this stage because family bias answers **how much responsibility** belongs to each channel, not the direction of the influence.

Direction is introduced later through the descriptor's live loading sign and descriptor activation.

---

## Descriptor Classification

Descriptors are classified using a margin-based dominance rule.

The current margin is:

```text
margin = 0.15
```

A channel is considered a real driver when its family-bias value lies within the margin of the descriptor's highest channel value.

The comparison is relative to the descriptor's own distribution rather than against an absolute global threshold.

The current classification produces:

| Family | Descriptor Count | Notes |
|---|---:|---|
| `Emotional` | 18 | Emotional appraisal responsibility |
| `Response` | 39 | Behavioral / action-output responsibility |
| `Persistence` | 13 | Structural; nonzero when Neuroticism is among the descriptor's selected top-2 traits |

A descriptor may belong to more than one family because the classification is based on channel dominance rather than exclusive assignment.

---

## Descriptor Activation

AB5C descriptor activation is calculated from the **live OCEAN vector**.

```text
descriptor_activation =
Σ(loading_i × trait_i)
/
Σ|loading_i|
```

where:

- `loading_i` = fixed AB5C loading for OCEAN trait `i`.
- `trait_i` = current live OCEAN value for trait `i`.

The result is bounded to:

```text
[-1, 1]
```

A positive value indicates activation toward the descriptor's positive pole.

A negative value indicates activation toward the descriptor's negative pole.

Descriptor activation is recomputed every tick because it depends on the current OCEAN state.

---

## Active Personality Descriptors

A descriptor participates in downstream processing only when its absolute activation exceeds:

```text
MINIMUM_ACTIVATION_THRESHOLD = 0.15
```

The activation test is:

```text
abs(descriptor_activation) > MINIMUM_ACTIVATION_THRESHOLD
```

This prevents weakly activated descriptors from unnecessarily affecting downstream layers.

---

## Trait-Level Emotional Bias Templates

Only traits with nonzero `emotional_bias` participate in the emotional expression mechanism:

- Openness
- Extraversion
- Agreeableness
- Neuroticism

Conscientiousness is structurally excluded.

Each participating trait has manually defined emotional-bias templates for its positive and negative poles.
The templates specify which of the eight base emotions are amplified or dampened.

### Pole Relationship

The negative pole is **not generally a clean inverse** of the positive pole.

| Trait | Positive Pole | Negative Pole | Inverse? |
|---|---|---|---|
| Neuroticism | Fear++, Sadness++, Anticipation++, Anger++, Trust--, Joy-- | Fear--, Sadness--, Anticipation--, Anger--, Trust++, Joy++ | Yes |
| Openness | Surprise-- | Surprise++, Fear++ | No |
| Extraversion | Joy++ | Anger++, Fear++, Disgust++, Sadness++, Joy-- | No |
| Agreeableness | Fear++, Sadness++, Disgust++, Anger-- | Anger++, Trust-- | No |


```text
negative_template[emotion] = -positive_template[emotion]
```

This symmetry is deliberate for Neuroticism.

The other three participating traits have independently defined negative-pole profiles because their negative poles contain distinct emotional effects rather than simply reversing the positive pole.

---

## Emotional-Bias Calibration Status

The direction and relative ordering of the emotional-bias relationships are research-traced using available personality–affect findings.

The absolute magnitude values are currently **placeholders**.

They are not treated as empirical effect sizes.

Final calibration is deferred until trained Neuron Layer output is available so that the Personality → Emotion influence can be scaled against real appraisal magnitudes.

---

## Descriptor Emotion DNA

Each descriptor receives a static emotional DNA signature.

The DNA is calculated once from the descriptor's AB5C loadings and the corresponding positive/negative trait templates.

```text
DNA[emotion] =
Σ(|loading_i| × template_i[emotion])
/
Σ|loading_i|
```

For each loading:

- If `loading_i >= 0`, use the trait's **positive-pole** template.
- If `loading_i < 0`, use the trait's **negative-pole** template.

The absolute loading is used as the weight:

```text
weight = abs(loading_i)
```

The loading sign is already consumed when selecting the positive or negative template.

Using the signed loading again would double-flip the direction of the effect.

Conscientiousness is excluded from both numerator and denominator when calculating emotional DNA.

This is a true exclusion rather than a zero-value dilution.

### Static vs. Live

Descriptor DNA is **static**.

It is computed once and represents the descriptor's inherent emotional signature.

Descriptor activation is **live** and is recomputed from the current OCEAN state.

Therefore:

```text
DNA = what the descriptor does
activation = how strongly the descriptor is switched on right now
```

---

## Personality → Emotion Influence

For every active emotional descriptor, live descriptor activation is multiplied by its static emotional DNA:

```text
live_influence[emotion] =
descriptor_activation × DNA[emotion]
```

The contributions of all active emotional descriptors are aggregated for each of the eight base emotions.

Conceptually:

```text
emotion_influence =
Σ(descriptor_activation × descriptor_emotional_DNA)
```

The result is a signed, magnitude-bearing Personality → Emotion influence vector.

Positive values increase the corresponding emotional tendency.

Negative values suppress it.

This is the actual live expression of personality into the emotional system.

> Memory does not directly create Personality → Emotion influence. Repeated emotional patterns first modify the OCEAN state. The live OCEAN state then determines descriptor activation, which combines with static descriptor DNA to produce the current emotional distortion.

---

# Part C — Persistence Bias

## Current Status

**Not yet built.**

Persistence bias is conceptually intended to make emotions linger through personality-dependent modification of the existing Neuron Layer decay system.

There is currently no separate persistence equation.

The intended mechanism is:

1. Identify currently active persistence-class descriptors.
2. Determine which emotions those descriptors implicate.
3. Translate those emotions into the relevant neuron-cluster activations.
4. Reduce the decay rate of the associated neurons.
5. Allow the affected emotional activation to persist longer than default decay.

The intended effect is **emotional lingering / rumination**, not behavioral persistence.

---

## Open Persistence Questions

The emotion-to-neuron translation is not yet fully defined.

The eight Plutchik-style base emotions and the eight Neuron Layer appraisal clusters are not a one-to-one mapping.

Therefore, a translation layer is required before persistence bias can be implemented reliably.

The current candidate for decay modification is multiplicative:

```text
decay_rate × (1 - persistence_bias)
```

This is preferred over an additive adjustment because it:

- Preserves a non-negative decay rate.
- Naturally scales the effect.
- Reduces the risk of runaway persistence.

The persistence mechanism remains future work until the emotion ↔ cluster correspondence is resolved.

---

# Part D — Response Bias

## Current Status

**Not yet designed.**

Response bias is the largest responsibility channel by descriptor coverage and is never structurally zero for any of the five OCEAN traits.

Conscientiousness is entirely routed through this channel:

```text
response_bias = 1.0
```

No response-selection equation or implementation has been finalized yet.

Response bias is therefore the next major expression mechanism to be designed after persistence bias.

---

# Status Summary

## Real / Locked

- Emotion → trait mapping.
- Core / supporting / contradicting emotion roles.
- Emotion-intensity zone conditioning.
- Net vote equation `P`.
- Pattern strength `G(M)`.
- Marginal contribution `ΔG`.
- Personality nudge equation.
- Boundary-safe OCEAN update.
- `RESPONSIBILITY_DISTRIBUTION`.
- Top-2/threshold hybrid descriptor trait selection.
- Margin-based descriptor family classification.
- Descriptor activation formula.
- Emotional-bias template structure.
- Positive and negative pole handling.
- Neuroticism exact inverse behavior.
- Descriptor DNA formula.
- Static DNA vs. live descriptor activation separation.
- Personality → Emotion live influence formula.

## Placeholder / Calibration Required

- `K` and `n` in `G(M)`.
- Absolute magnitude values inside `EMOTIONAL_BIAS_TEMPLATES`.
- Final emotional-bias calibration against trained Neuron Layer output.

## Work in progress

- Persistence bias mechanism.
- Response bias mechanism.

