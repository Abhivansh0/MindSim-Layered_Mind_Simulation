# MindSim — Continuity of Mind: Why the System Never Resets

## The Problem This Doc Explains

A naive stimulus-response system processes each stimulus in isolation: a stimulus arrives, the system computes a response, and the internal state returns to some fixed baseline before the next stimulus arrives. Nothing carries over. A traumatic event and a pleasant one, arriving back to back, would be treated as two completely independent computations — the mind "forgets" the first the moment it starts processing the second.

This is not how MindSim behaves, and it wasn't made to behave this way by adding a memory of "what just happened" that gets checked before each new response. **No layer in MindSim explicitly codes emotional persistence as a feature.** Continuity is an emergent property — a side effect of several mechanisms that were each built for other reasons, but which happen to share one property in common: **they operate on time, not on stimulus events.**

This doc exists to make that emergence visible, since it isn't obvious from reading any single layer's code in isolation.

---

## The Naive Model, and Why MindSim Doesn't Work That Way

In a stateless design, every stimulus would trigger something like:

1. Reset relevant internal values to baseline.
2. Process the current stimulus in isolation.
3. Produce a response.
4. Discard everything, ready for the next stimulus.

If MindSim worked this way, a person who just experienced something frightening, followed immediately by something joyful, would respond to the joyful stimulus as if the frightening one never happened — no lingering unease, no bleed-through, nothing carried forward. This is psychologically implausible. Real minds don't reset between experiences; a frightened person who is then told good news is still, at least for a while, a frightened person hearing good news, not a blank slate hearing good news.

MindSim avoids this not by adding a rule that says "remember the last emotional state and factor it in" — no such rule exists anywhere in the system. Instead, several independent mechanisms are each built around **decay that runs on elapsed time**, not on "did a new stimulus arrive." Because none of them are reset by the arrival of a new stimulus, whatever they were doing when the last stimulus was processed is often still partway through happening when the next one starts.

---

## Mechanism 1: Neuron Decay

Neuron activations in the Neuron Layer decay according to their own per-cluster decay rate, measured against elapsed time. A neuron cluster that fired strongly in response to one stimulus does not immediately drop back to zero the instant that stimulus finishes processing — it decays gradually, on its own clock.

This means that if a second stimulus arrives before a previously-activated cluster has fully decayed, that cluster is **still partially active** when the new stimulus is being appraised. The new stimulus doesn't start from a clean slate — it starts from whatever activation state the previous stimulus left behind, now partially decayed but not gone.

Practically: if a threat-relevant cluster was strongly activated by a frightening event, and a happy stimulus arrives shortly after, that threat cluster may still carry meaningful residual activation. The appraisal of the new, happy stimulus is computed *on top of* that residual activation, not from zero.

---

## Mechanism 2: Hebbian Bond Decay

Synaptic bonds formed between co-activated neuron clusters (see: streak-based Hebbian bond formation) also decay on their own time-based schedule, independent of whether a new stimulus has arrived. A bond that has recently strengthened doesn't reset or weaken the moment stimulus processing moves on to something new.

This means associative relationships built from recent experience remain available to influence how a subsequent, unrelated stimulus gets processed — through pre-activation boosting — for as long as the bond itself hasn't decayed, regardless of how many stimuli have been processed in between.

---

## Mechanism 3: Emotional Inertia

The Emotion Layer does not snap emotion values directly to whatever a given tick's appraisal computes. Each emotion moves toward its computed target value at its own inertia rate, meaning a strongly-felt emotion doesn't vanish the instant the triggering appraisal stops being reinforced — it decays toward the new target gradually, at a rate specific to that emotion.

If fear is strongly elevated by one stimulus, and the very next stimulus is unrelated and mildly positive, fear does not reset to its baseline before the next tick's blending happens. It moves toward whatever the new appraisal computes, but starting from its still-elevated position — meaning genuine fear can still be present, measurably, while a happy stimulus is simultaneously being processed.

---

## How These Combine

None of these three mechanisms references the others, and none of them contain any explicit logic checking "has a new stimulus arrived, should I reset." Each one simply decays or moves toward a target based on elapsed time. Because a new stimulus can arrive before any of these time-based processes have finished settling, whatever state they were in from the previous stimulus is still present — to varying degrees — when the next stimulus begins.

This produces the observed behavior: a mind that has just experienced something traumatic does not appraise the next, unrelated stimulus as if nothing happened. Elevated threat-related neuron activation, strengthened associative bonds, and an emotion that hasn't yet decayed back down all persist into the next tick's processing, coloring it — without any layer explicitly modeling "persistence" or "carryover" as its own feature.

**Continuity of mind, in MindSim, is not a mechanism. It is the absence of a reset.**

---

## Why This Matters for Realism

This is a direct instance of MindSim's core design philosophy: simulate realistic behavior by finding where complexity is *earned*, rather than manufacturing it directly. A hand-coded "emotional carryover" system would have required its own rules for how much carries over, for how long, and under what conditions — a whole new mechanism, with its own parameters to tune and justify.

Instead, the three mechanisms described above already existed for independent, well-motivated reasons — realistic neuron decay, genuine associative learning, and smooth (rather than jarring) emotional transitions. Continuity of mind fell out of these for free, simply because none of them happen to be gated on stimulus boundaries. This is the kind of emergent realism the architecture is built to favor over explicitly engineered behavior wherever a genuine mechanism can produce the same result on its own.
