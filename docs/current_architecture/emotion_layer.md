# Emotion Layer

## Responsibility

The emotion layer receives the `activation_map` from MindState and produces a dynamic emotional state. It generates 8 base emotions using cluster profiles, applies regulation, tracks trends, moves emotions gradually via inertia, checks intensity, compounds base emotions into complex emotions, and identifies the dominant emotion.

---

## Processing Pipeline

1. Receive `activation_map` from MindState.
2. Run `Process_Emotions` — score each base emotion against its cluster profile.
3. Store scores into `target_emotion_tank`.
4. Run `Regulate_Emotions` — apply suppressors and releasers.
5. Run `Trend_Check` — determine direction of emotional change.
6. Run `Update_Inertia` — move current emotion state gradually toward target values.
7. Run `Intensity_Check` — relabel base emotions based on strength.
8. Run `Compound_Emotion` — form complex emotions from base emotion pairs.
9. Determine `Dominant_Emotion`.

---

## Base Emotions

Based on **Plutchik's Wheel of Emotions**:

| Emotion | Low Intensity | Ideal | High Intensity |
|---|---|---|---|
| Fear | Apprehension | Fear | Terror |
| Anger | Annoyance | Anger | Rage |
| Joy | Serenity | Joy | Ecstasy |
| Sadness | Pensiveness | Sadness | Grief |
| Trust | Acceptance | Trust | Admiration |
| Disgust | Boredom | Disgust | Loathing |
| Anticipation | Interest | Anticipation | Vigilance |
| Surprise | Distraction | Surprise | Amazement |

---

## Emotion Profiles (Current — Evidence Accumulation Based)

Each base emotion is defined by an **emotion schema** consisting of three components:
`core` - the primary appraisal required for the emotion to be psychologically plausible.
`supporting` - appraisals that positively contribute to the emotion.
`contradicting` - appraisals that suppress the emotion.

**Example — Fear schema:**
```
fear = {
  core:          threat
  supporting:    [novelty, urgency, discomfort]
  contradicting: [familiarity, reward] 
}
```

> Note: These schemas are intentionally minimal. The goal is to preserve psychological distinctiveness between emotions while allowing complex emotional states to emerge naturally.

---

## Process_Emotions

`Process_Emotions` follows an **evidence accumulation architecture** rather than range-based profile matching.

For each base emotion:

### Step 1 — Collect Positive Evidence

Positive evidence consists of:

- The `core` appraisal (if active).
- All active `supporting` appraisals.

The `core` appraisal participates in the positive evidence pool rather than acting as a hard gate.

```text
support_total = core + active_supporting_clusters

positive =
support_total / (total_supporting_clusters + 1)
```

Missing supporting appraisals contribute `0`.

---

### Step 2 — Collect Contradictory Evidence

Contradicting appraisals suppress the emotion signal.

```text
contradicting = sum(active_contradicting_clusters) / total_contradicting_clusters
```

Missing contradicting appraisals contribute `0`.

---

### Step 3 — Generate Emotion Signal

The base emotion signal is generated using the accumulated evidence.

```text
emotion_signal = positive * (1 - contradicting)
```

Contradicting appraisals continuously suppress the emotion rather than completely blocking it.

---

### Step 4 — Apply Core Penalty

If the `core` appraisal is absent from the `activation_map`, the emotion is considered psychologically implausible but not impossible.

A soft penalty is applied.

```text
emotion_signal *= 0.5
```

This is intentionally a **soft enforcement** rather than a hard requirement.

---

### Step 5 — Clamp Values

```text
emotion_signal = max(0, min(emotion_signal, 1))
```

The final value is stored inside `target_emotion_tank`.

> **Design Principle:** The emotion layer no longer asks *"What does fear look like?"*. Instead, it asks *"What evidence exists for fear?"*. Emotions are treated as emergent states that arise from accumulated appraisal evidence rather than pattern matches against predefined profiles.


---

## Target Emotion Tank

The `target_emotion_tank` stores the reflexive emotional response to a stimulus — the **target** the emotional state is moving toward. The actual current emotion state does not jump immediately to this target; it moves toward it under inertia.

---

## Regulate_Emotions

Each base emotion has suppressor and releaser emotions defined in the emotion mapping.

**Example — Anger:**
- Suppressed by: `Trust`
- Released by: `Anticipation`

**Formulas:**
```
suppress_value = target_emotion_tanks[suppress_emotion] * SUPPRESSION_STRENGTH
release_value  = RELEASE_STRENGTH * (1 - target_emotion_tanks[release_emotion])
```

Regulation values are collected first, then applied in a single batch — same pending pattern as `Pre_Activation_Boost` — to avoid order-of-evaluation contamination.

---

## Trend_Check

Compares newly generated emotion values in `target_emotion_tank` against existing values to compute the **direction** of the emotion vector (rising, falling, stable).

> Future plan: track actual flow of emotion through inertia values rather than comparing raw tank values directly.

---

## Update_Inertia

Solves the continuous-state problem of sudden emotional jumps. Instead of snapping to `target_emotion_tank`, each emotion moves gradually toward its target under its individual **inertia rate**.

This creates the **lingering emotional effect** — an emotion that was strongly activated continues to persist and fade gradually rather than disappearing instantly.

> Current known issue: inertia rates are set too high, causing emotions to converge too quickly. Tuning is deferred because neuron decay already contributes lingering via the activation map — the two mechanisms produce an emergent combined effect. Whether explicit inertia tuning is necessary remains an open question.

---

## Intensity_Check

Once an emotion reaches its target value, its strength determines which intensity label is applied (e.g., low anger = Annoyance, ideal anger = Anger, high anger = Rage).

---

## Compound_Emotion

Complex emotions emerge from combinations of base emotions when both parent emotions exceed a defined threshold simultaneously.

**Example:**
```
Joy + Trust → Love
```

---

## Dominant_Emotion

After compounding, the dominant emotion — the single strongest active emotional signal — is identified and recorded in MindState.
