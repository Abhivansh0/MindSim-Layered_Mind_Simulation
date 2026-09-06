# ADR-012: Distributing Descriptors Across Emotional, Persistence, and Response Channels

**Status:** Accepted

---

## Context

Each OCEAN trait distributes its downstream influence across three channels — emotional distortion, emotional persistence (how long emotions linger, not behavioral persistence), and behavioral response — with a fixed weighting per trait.

Each of the 44 AB5C descriptors is itself a blend of multiple OCEAN traits, so each descriptor ends up with its own blended weighting across the same three channels. The problem: every descriptor received a nonzero value in all three channels by construction, since a weighted blend across several traits can only land exactly at zero if every contributing trait is independently zero in that channel.

This meant a single fixed cutoff for "does this descriptor meaningfully belong to this channel" behaved inconsistently depending on the channel. One channel is numerically dominant for most traits and cleared almost any reasonable fixed cutoff for nearly every descriptor, while a different channel is fed by only a single trait and rarely cleared the same cutoff for any descriptor. No one fixed number could meaningfully separate signal from noise across both.

A further, more specific issue arose for the single-trait-fed channel: comparing its value against a descriptor's own strongest channel (a relative rather than absolute test) would systematically exclude descriptors where that one contributing trait is genuinely present but not the descriptor's dominant characteristic — even though its mere presence is fully informative on its own, since there is only one possible source for that channel at all.

---

## Decision

Classify descriptor channel membership using two different tests, chosen deliberately per channel based on how many traits actually feed into it:

- For channels fed by multiple traits, membership is decided **relative to each descriptor's own strongest channel** — a channel counts as a real driver only if it's close to that descriptor's own top value, not compared against a fixed number or against other descriptors.
- For the channel fed by only a single trait, membership is decided by **simple presence** — a descriptor belongs to that channel if the value is nonzero at all, since there is no risk of an accidentally-nonzero result the way there is when multiple traits are blended together.

Full implementation details, including the exact threshold values used, are documented in `docs/personality_layer.md`.

---

## Alternatives Considered

- **A single fixed cutoff applied identically across all three channels:** Rejected — the numerically dominant channel cleared almost any reasonable fixed cutoff for nearly every descriptor, while the single-trait-fed channel almost never did, making one number unable to meaningfully separate signal from noise in both cases.
- **Always selecting a fixed number of top descriptors per channel, regardless of their actual values:** Rejected — this would force descriptors into a channel even during a period where none are genuinely characteristic of it.
- **Applying the same relative-to-own-strongest-channel test to the single-trait-fed channel as well:** Rejected — this systematically undercounts descriptors for which the single contributing trait plays a real, meaningful role but isn't the descriptor's single strongest characteristic. A relative test measures dominance; for a channel with only one possible source, mere presence is the more informative signal.

---

## Consequences

### Benefits

- The two dominant, multi-trait-fed channels reflect genuine relative dominance within each descriptor's own profile, rather than being distorted by the fact that raw magnitudes differ systematically across channels.
- The single-trait-fed channel correctly captures every descriptor where that trait plays a real role, producing a smaller but more structurally meaningful set than a relative test would have.
- The reasoning for testing channels differently is made explicit, rather than silently applying one method everywhere and accepting whatever falls out.

### Tradeoffs

- The margin used for the relative test is itself an unvalidated constant, chosen for reasonable-looking behavior on inspection rather than derived from an external benchmark.
- The presence-based test for the single-trait-fed channel would need to be revisited if a second trait were ever given a nonzero weight in that channel, since presence alone would no longer cleanly indicate which trait was responsible.
- Testing channels differently means the classification logic is less uniform than a single global rule would be, which is why this decision is documented explicitly rather than left implicit in the code.
