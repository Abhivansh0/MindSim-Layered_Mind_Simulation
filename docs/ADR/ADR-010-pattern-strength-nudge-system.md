# ADR-010: Pattern-Strength Nudge System for OCEAN Formation

**Status:** Accepted

---

## Context

The Personality Layer required a mechanism for repeated emotional patterns to actually shift the OCEAN vector over time.

Three separate design questions needed resolution, each with a rejected first attempt:

**How should accumulated memory count translate into pattern strength?**
The Memory Layer's existing base-level activation (BLA) was considered as a reusable signal, since it already measures how "strong" a memory is. This was rejected: BLA measures *retrievability* — how easily a memory can be recalled — not *formative influence* on personality. A worked example (a strong, life-shaping memory that should retain personality influence indefinitely) showed BLA naturally decays toward zero over time for exactly the kind of memory that should keep shaping personality, proving the two quantities are not interchangeable.

**What shape should pattern strength take as memory count grows?**
An initial growth curve produced its single largest effect from the very first reinforcing memory, tapering immediately afterward. This contradicted the intended behavior: a handful of memories shouldn't meaningfully move personality (not enough evidence yet), and an already-massive, long-established pattern shouldn't move it further either (already fully proven) — only a pattern's middle life, while it's still being established, should carry the most weight.

A two-stage alternative was also considered: keep the original growth curve, and layer a separate bell-shaped weighting on top to force the desired middle-loaded behavior. This was rejected — it requires tuning two independent curves with no guarantee they'd agree with each other, and reintroduces exactly the kind of arbitrary hand-placed peak the simpler single-curve fix was meant to avoid.

**How much of a pattern's accumulated strength should apply on each new event?**
Reapplying a pattern's *entire* current strength every time it's touched was confirmed correct in principle — this is what allows compounding/sensitization to work as intended. But applying the full value on every touch, rather than only what's newly changed, would mean a pattern's 300th reinforcing memory injects a nudge just as large as its 3rd — which defeats the entire point of the growth curve.

---

## Decision

Adopt a single growth curve for pattern strength whose shape naturally produces the intended "middle matters most" behavior without a second, independently-tuned curve — and apply only the *change* in strength produced by each new event, not the pattern's full accumulated value.

Direction of the nudge is determined by a normalized vote across whichever emotions are active in the pattern, weighted by each emotion's role (core / supporting / contradicting) for the trait in question and its intensity at the time — allowing the same emotion to contribute differently to the same trait depending on how intensely it's expressed.

The resulting nudge is applied to the OCEAN vector using a boundary-aware update that slows movement as a trait approaches either end of its valid range, scaled to the correct boundary depending on the nudge's direction.

Full implementation details, including the exact equations, are documented in `docs/personality_layer.md`.

---

## Alternatives Considered

- **Reusing Memory Layer base-level activation as the pattern-strength signal:** Rejected — retrievability and formative influence are different quantities; a memory can lose retrievability while its personality-shaping effect should persist or even compound.
- **A plain diminishing-returns growth curve:** Rejected — produces its largest effect at the very first reinforcing memory rather than in the pattern's middle life, contradicting the intended saturation behavior at both ends.
- **An independent bell-shaped weighting layered on top of a diminishing-returns curve:** Rejected — introduces a second, separately-tuned curve with no guarantee of internal consistency, and reintroduces an arbitrary peak parameter the single-curve approach specifically avoids.
- **Reapplying a pattern's full accumulated strength on every touch:** Rejected as the per-event application method — while full recomputation of the pattern's overall strength is necessary and correct, using that full value as the nudge on every event means late-life memories would nudge just as hard as early ones.
- **An unsigned boundary-safety adjustment applied the same way regardless of nudge direction:** Rejected — OCEAN traits range from a negative to a positive extreme, not zero to one; a boundary-safety term that doesn't account for which direction a trait is moving produces the opposite of its intended effect near the negative extreme.

---

## Consequences

### Benefits

- A single growth curve produces both correct long-run pattern strength and correct middle-loaded marginal nudging, avoiding the risk of two independently-tuned mechanisms disagreeing with each other.
- Applying only the change in pattern strength per event, rather than the pattern's full value, means already-established patterns naturally stop contributing large nudges without needing separate logic to detect "this pattern is done forming."
- The same emotion can meaningfully play different roles for the same trait depending on its intensity, without requiring separate architecture beyond the existing role-mapping structure.
- Boundary-safe application guarantees traits stay within their valid range regardless of how many patterns nudge the same trait in the same tick.

### Tradeoffs

- The growth curve's steepness and inflection point are currently placeholder constants, not yet calibrated against real data.
- The relative weighting of emotion roles and intensity levels is likewise placeholder — only the ordering between them is currently defensible, not the exact magnitudes.
