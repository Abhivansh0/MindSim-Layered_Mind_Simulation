# ADR-013: Emotion-Weighted Memory Decay
**Status:** Accepted

---
## Context
MindSim's memory layer needs a way to decide how quickly a stored memory
fades over time. The initial approach used classic ACT-R style decay,
where every memory forgets at the **same fixed rate**, regardless of
what it was about.

Testing against how human memory actually behaves showed this was wrong:
emotionally significant experiences tend to stick around much longer
than plain, uneventful ones. A fixed decay rate has no way to represent
that — a highly emotional memory and a completely neutral one would fade
at exactly the same speed, which doesn't hold up.

A naive fix of just scaling decay rate linearly with emotional weight
was also considered and rejected: it would treat every small emotional
difference as equally meaningful, when really only the strongly
emotional (or strongly neutral) memories should stand out.

---
## Decision
Make the decay rate **per-memory** and driven by that memory's emotional
weight, instead of a single fixed rate for everything:
- Emotionally **neutral** memories decay at close to the normal/default
  rate.
- Emotionally **weighted** memories (positive or negative extremes)
  decay **slower**, so they persist longer — mirroring how emotional
  experiences stick in human memory.
- Memories with **middling/unclear** emotional weight are kept close to
  the normal rate, so the system doesn't overreact to small or noisy
  emotional signal.
- Only at the extremes does emotional weight meaningfully pull the decay
  rate away from normal — the effect is deliberately non-linear so
  "somewhat emotional" doesn't get treated the same as "very emotional."

---
## Alternatives Considered
- **Fixed decay rate (classic ACT-R):** Rejected — has no concept of
  emotional salience; every memory forgets identically.
- **Linear scaling of decay rate by emotional weight:** Rejected — treats
  every unit of emotional weight as equally significant, which
  overreacts to small/ambiguous emotional differences instead of
  reserving the effect for genuinely strong emotional memories.

---
## Consequences

**Benefits:**
- Emotionally significant memories persist longer, matching how memory
  is expected to behave.
- Neutral or ambiguous memories aren't over-affected by noisy emotional
  signal — only strong emotional weight meaningfully changes the decay
  rate.
- Drops into the existing decay math as a straightforward substitution,
  with no other part of the memory system needing to change.

**Tradeoffs:**
- How strongly emotional weight is allowed to shift the decay rate was
  chosen by intuition, not fit to real data — it should be revisited
  once there's actual usage to tune against.
- If emotional weight tagging tends to cluster near neutral for most
  memories, the effect will barely show up in practice, since the
  formula is deliberately insensitive in that middle range.
- Moves away from a well-studied, fixed-parameter cognitive model, so
  there's less existing research to lean on when debugging or tuning
  decay behavior going forward.
