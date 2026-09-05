# ADR-011: Descriptor Emotional DNA — Static Signature Separated from Live Activation

**Status:** Accepted

---

## Context

Personality's live expression into emotion required a way for each of the 44 AB5C descriptors to produce a concrete, per-emotion distortion of live appraisal.

Two quantities were initially conflated:

- What a descriptor's emotional character *is* — which emotions it amplifies or dampens, given its underlying OCEAN loadings.
- How strongly that descriptor is *currently expressed*, given the live OCEAN vector at this moment.

Computing both fresh together on every tick was considered but rejected. A descriptor's underlying character doesn't change tick to tick — only the live OCEAN state does. Recomputing the full signature every tick would be wasted work, and would make it harder to tell whether an incorrect result comes from the descriptor's underlying character being wrong or from its current activation being wrong.

A related issue came from OCEAN traits being able to take both positive and negative values. A descriptor's loading on a trait can itself be positive or negative, and research review established that most traits' negative poles are not simply a mirror image of their positive poles. This meant a descriptor loading negatively on a trait needed to pull from that trait's distinct negative-pole emotional profile, not just flip the sign of its positive-pole profile.

A further bug surfaced during implementation: once a positive or negative profile is selected based on a loading's sign, using the loading's sign again as part of the weighting calculation silently double-flips the result.

---

## Decision

Separate descriptor emotional character into two explicitly distinct artifacts, computed at different times for different purposes:

- A **static signature**, computed once per descriptor from its OCEAN loadings and each relevant trait's emotional profile, using the loading's sign only to select which of a trait's two poles applies — never reusing that sign a second time in the weighting itself.
- A **live activation**, recomputed every tick from the current OCEAN state, representing how strongly the descriptor is currently expressed.

The descriptor's actual live contribution to emotional appraisal is the static signature scaled by the live activation. The signature answers what the descriptor would do if fully expressed; the activation answers how close to fully expressed it currently is.

Full implementation details, including the exact formulas, are documented in `docs/personality_layer.md`.

---

## Alternatives Considered

- **Recomputing a descriptor's full emotion-distortion signature fresh on every tick, combined directly with the live OCEAN state in a single pass:** Rejected — conflates a static property with a dynamic one, making both harder to verify independently, and performs unnecessary repeated work on the part of the calculation that never changes.
- **Reusing a loading's sign both to select a pole-specific profile and again as part of the weighting:** Identified as an active bug during implementation review — this double-consumes the sign, silently negating results a second time. Corrected to use the loading's magnitude only as the weight, with direction coming entirely from which profile was selected.
- **Treating a trait's negative-pole emotional profile as the simple negation of its positive-pole profile across the board:** Rejected for most of the emotionally-relevant traits, based on research review showing their negative poles carry a genuinely distinct emotional character rather than a mirror image. Only one trait was confirmed to behave as a clean inverse.

---

## Consequences

### Benefits

- A descriptor's static signature can be computed once and reused, rather than recomputed every tick — the only per-tick cost is the cheaper activation calculation.
- Separating "what a descriptor does" from "how active it is" makes each independently verifiable — an error in one produces a distinguishable symptom from an error in the other.
- Correctly threading a loading's sign through profile-selection, rather than through the weighting, avoids a class of silent double-negation errors that would otherwise produce plausible-looking but wrong results.
- Descriptors whose negative-pole expression differs meaningfully from their positive-pole expression are modeled with their own distinct character, rather than an assumed mirror image.

### Tradeoffs

- A descriptor's static signature depends on trait-level emotional profiles that remain placeholders in their exact magnitudes, pending further calibration. The separation itself is correct and stable; the numeric output built on top of it is still under active research.
- Some traits currently have thinner or less-confirmed emotional profiles than others, meaning descriptors drawing heavily on those traits inherit a comparatively weaker evidence base.
- The static/live split assumes a descriptor's OCEAN loadings are themselves fixed. If those loadings are ever revised, every cached static signature depending on them must be regenerated.
