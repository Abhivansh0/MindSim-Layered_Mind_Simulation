# Memory Layer

## Responsibility

The memory layer stores every stimulus/response event as a `Memory` record, tagged with a snapshot of the emotional state at the time it was formed. It links each new memory to related existing memories along three independent channels — temporal, semantic, and emotional — and, on later stimuli, retrieves the memories most relevant to the current moment using an ACT‑R‑derived base‑level‑activation model combined with relevance scoring and spreading activation across those same three link types.

Storage and retrieval are two distinct flows through the same layer, backed by a ChromaDB collection (`mindsim_memories`, cosine space) as the persistence store.

---

## The Memory Record

| Field | Description |
|---|---|
| `id` | UUID |
| `stimulusSummary` / `responseSummary` | Text summaries of the event |
| `stimulusVector` | Embedding of the stimulus (from `mindState.stimulus_vector`) |
| `emotionMap` | Snapshot of base + compound emotion values at formation time |
| `initialEmotionalWeight` | Scalar salience of the event (see [Emotional Weight](#emotional-weight)) |
| `createdAt` | Formation timestamp |
| `recallHistory` | Timestamps of every subsequent successful recall |
| `emotionContext` | Bucketed L/M/H signature string of the emotion snapshot (see [Emotion Context](#emotion-context--context-boxes)) |
| `temporalLinks` / `semanticLinks` / `emotionalLinks` | `{ neighborId: strength }` maps, one per channel |

---

## Processing Pipeline

### Storage flow (`createMemory`)

1. Take the current stimulus vector and a snapshot of the emotional state from MindState.
2. Compute `initialEmotionalWeight` from that snapshot.
3. Compute the `emotionContext` bucket-string from that snapshot.
4. Persist the new `Memory` into the ChromaDB collection.
5. Run `establishLinksForNewMemory` — find temporal, semantic, and emotional neighbors and write links bidirectionally.
6. Register the memory in its `emotionContext` box.

### Retrieval flow (`retrieveMemories`)

1. Get semantic candidates for the current stimulus vector (ChromaDB nearest-neighbor query).
2. Get emotional candidates for the current emotional state (context-box match).
3. Merge both into one candidate pool.
4. Snapshot the currently "active" memories (from the *previous* retrieval round) for spreading activation, then prune stale ones.
5. For each candidate: compute unified relevance, base-level activation (BLA), and spreading activation from active neighbors along each link type; sum into a total retrieval activation.
6. Keep candidates whose activation clears the retrieval threshold; record a successful recall for each.
7. Expand one hop via each recalled memory's stored links to pull in associatively-activated memories.
8. Add everything recalled or associatively activated this round into the active set, for the *next* retrieval's spreading activation.

---

## Storage

### Emotional Weight

`calculateEmotionalWeight` scores how salient an event was, from the emotional state active when it was formed:

```text
peak           = max(all base + compound emotion values)
activeAverage  = mean(base emotion values >= ACTIVE_EMOTION_THRESHOLD)   # 0 if none active
complexity     = min(numCompoundEmotions * COMPOUND_BONUS, COMPLEXITY_CAP)

emotionalWeight = (peak * 0.65) + (activeAverage * 0.25) + complexity
```

Clamped to `[0, 1]`. `ACTIVE_EMOTION_THRESHOLD = 0.30`, `COMPOUND_BONUS = 0.08`, `COMPLEXITY_CAP = 0.20`.

This weight becomes the memory's `initialEmotionalWeight`, which later controls how quickly it decays (see [Decay Parameter](#decay-parameter)).

### Emotion Context / Context Boxes

`computeEmotionContext` reduces an emotion snapshot to a compact signature: each **base** emotion (sorted by name) is bucketed into `L` / `M` / `H`:

```text
bucketLetter(v):
  v < LOW_MEDIUM_THRESHOLD (0.33)   -> "L"
  v < MEDIUM_HIGH_THRESHOLD (0.66)  -> "M"
  else                              -> "H"
```

The concatenated letters (one per base emotion) form the `emotionContext` string, e.g. `"LMHLLMHL"`. Only base emotions participate — compounds are excluded from the signature.

All memories sharing an identical context string live in the same **context box** (`contextBoxes: { context -> [memoryIds] }`). Boxes are rebuilt once at startup from persisted metadata (`loadContextBoxes`) and maintained incrementally after that (`registerMemoryInContextBox`) rather than being rescanned on every retrieval.

Context strings are compared to each other by converting letters to numeric values (`L=0.15, M=0.5, H=1.0`) and taking cosine similarity between the resulting vectors (`contextToVector` + `cosineSimilarity`) — this is what lets a stimulus match a *nearby* emotional signature, not only an identical one.

### Establishing Links

For a new memory, `establishLinksForNewMemory` gathers neighbor candidates from three independent channels and writes each as a link:

| Channel | Candidate source | Notes |
|---|---|---|
| Temporal | `getTemporalCandidates` — other memories created within the temporal window of `createdAt` | Strength from time-decay, see below |
| Semantic | `getSemanticLinkCandidates` — ChromaDB nearest-neighbor query on the stimulus vector | Same threshold as retrieval-time semantic candidates |
| Emotional | `getEmotionalCandidates` — memories in context boxes similar enough to this memory's own box | The memory's own box excluded from its own candidate list |

`writeLinkPair` writes each link **undirected**: the strength is stored on both the new memory and the neighbor's own metadata, and both records are persisted. This is a deliberate contrast with the Neuron layer's Hebbian synapses, which are strictly unidirectional (`source → target`) — memory links carry no source/target asymmetry.

> Open question: the Personality layer's formation mechanism (`G(M)`, `ΔG`) assumes memories are linked to a shared **signature node**, but no such concept exists here. The closest analogues are the `emotionContext` context-box grouping and this temporal/semantic/emotional link graph — neither is a direct match. This mapping needs to be resolved before Personality-layer formation can run against real memory data.

### Context Window

`updateContextWindow` maintains a rolling deque (`MAX_CONTEXT_WINDOW = 5`) of recent `{stimulus, response, timestamp}` entries, separate from ChromaDB — a short-term buffer rather than a persisted memory.

> Current status: nothing in this layer reads from `self.contextWindow` yet — it isn't wired to retrieval, linking, or scoring. Presumably intended as short-term working context for another layer to consume.

---

## Candidate Generation

### Semantic Candidates

`getSemanticCandidates` (used at **retrieval** time, against the live stimulus) and `getSemanticLinkCandidates` (used at **storage** time, to link a new memory to existing ones) both query ChromaDB for up to `SEMANTIC_CANDIDATE_LIMIT` (30) nearest neighbors by embedding, convert distance to similarity (`similarity = 1 - distance`), and discard anything below `SEMANTIC_CANDIDATE_THRESHOLD` (0.5).

### Emotional Candidates

`getEmotionalCandidates` computes the current emotion snapshot's context string and vector, compares it against every existing context box via cosine similarity, and — for any box scoring at or above `EMOTION_CONTEXT_SIMILARITY_THRESHOLD` (0.85) — adds every memory in that box as a candidate with the box's similarity score. Returns the top `EMOTIONAL_CANDIDATE_LIMIT` (30) by score.

### Merging

`mergeCandidates` unions the semantic and emotional candidate pools into a single dict per memory, filling in `0.0` for whichever relevance type a given candidate didn't come from.

---

## Temporal Linking

Temporal link strength decays exponentially with elapsed time, using a half-life:

```text
temporalDecayRate = ln(2) / TEMPORAL_HALF_LIFE          # half-life = 30 (minutes)
strength(Δminutes) = e^(-temporalDecayRate * Δminutes)
```

The **temporal window** — how far apart two memories can be and still be considered for a link — is derived from the minimum strength worth keeping, rather than hardcoded:

```text
temporalWindowMinutes = ln(1 / MINIMUM_TEMPORAL_LINK_STRENGTH) / temporalDecayRate
```

With `MINIMUM_TEMPORAL_LINK_STRENGTH = 0.1`, this works out to roughly 100 minutes on either side of a memory's creation time. `getTemporalCandidates` queries ChromaDB metadata for memories with `createdAtEpoch` inside that window and keeps any whose computed strength clears the minimum.

---

## Relevance

`calculateUnifiedRelevance` combines semantic and emotional relevance for a candidate using a probabilistic-OR:

```text
unifiedRelevance = semantic + emotional - (semantic * emotional)
```

This keeps the result bounded to `[0, 1]` while giving diminishing returns to a candidate that's already strong on one channel and also matches on the other. Note there is no equivalent "temporal relevance" term here — temporal proximity is not evaluated directly between the live stimulus and a candidate; it only enters retrieval through spreading activation from currently active memories (see [Spreading Activation](#spreading-activation)).

---

## Accessibility (Base-Level Activation)

Modeled on ACT‑R's base-level activation equation: activation grows with the number of times a memory has been referenced (created + every recall) and decays with time since each reference.

### Decay Parameter

Each memory's decay rate `d` is derived from its own `initialEmotionalWeight`, not fixed globally:

```text
d(w) = 0.5 - 0.2 * (2w - 1)^3,   clamped to [MIN_DECAY_PARAMETER, MAX_DECAY_PARAMETER] = [0.3, 0.7]
```

| `initialEmotionalWeight` | `d` |
|---|---|
| 0.0 (unremarkable) | 0.7 (fastest decay) |
| 0.5 (neutral) | 0.5 (ACT‑R default) |
| 1.0 (maximally salient) | 0.3 (slowest decay) |

Emotionally weightier memories are therefore modeled as more durable — they resist forgetting longer than neutral ones.

### Base-Level Activation (BLA)

```text
BLA = ln( Σ over {createdAt} ∪ recallHistory of  elapsedDays^(-d) )
```

Every reference to the memory — its original formation and every later recall — contributes a term; more references raise BLA (a practice/testing effect), while each term individually decays with `elapsedDays^(-d)`. `MIN_ELAPSED_DAYS_EPSILON` (1e‑6) floors `elapsedDays` to avoid a divide-by-zero/`0^(-d)` blowup when a reference is effectively simultaneous with the current query.

---

## Retrieval

### Spreading Activation

Before scoring candidates, `pruneActiveChunks` drops anything from `activeChunks` older than the temporal window, then the remaining `activeChunkIds` is fixed as a **snapshot taken before this round's own results exist**. Each candidate's spread contribution sums the strength of its links (temporal, semantic, emotional — each computed separately) to whatever is in that snapshot:

```text
spreadX(memory) = Σ strength for each linkX neighbor that is in activeChunkIds
```

Taking the snapshot before this round's results are computed is deliberate: a candidate can only be boosted by genuinely prior activity, never by something only just recalled in the same pass.

### Retrieval Activation

```text
activation = unifiedRelevance + BLA + spreadTemporal + spreadSemantic + spreadEmotional
passes     = activation >= RETRIEVAL_ACTIVATION_THRESHOLD   # 0.5
latency    = LATENCY_FACTOR * e^(-activation)                # LATENCY_FACTOR = 0.3
```

Higher activation means both a higher chance of passing the retrieval criterion and a lower (faster) retrieval latency.

> Calibration status: the only tuning knob for latency is the single `LATENCY_FACTOR` constant (0.3). It produces a correct relative ordering — higher activation is always faster — but isn't tied to any measured or target time scale.

### Associative Expansion

Candidates that clear the threshold are recorded as successful recalls (`recordSuccessfulRecall` — append to `recallHistory`, persist). `expandViaMemoryLinks` then does exactly **one hop** outward from that recalled set: for every link (temporal, semantic, emotional) stored on a recalled memory, any neighbor not already in the recalled set is pulled in as "associatively activated," tagged with which memory and link type brought it in.

Associatively-activated memories bypass the retrieval-activation threshold entirely — they're included purely because a memory that did clear the bar happens to be linked to them. They still count as genuine recalls: their `recallHistory` is updated and persisted, same as a directly-recalled memory. The expansion never cascades past this single hop.

Both the directly recalled and the associatively-activated sets are added into `activeChunks` at the end of the round, becoming the spreading-activation source for the *next* retrieval call.

### Output

```text
retrieveMemories(...) -> {
  "recalled":               [ { id, summaries, emotionMap, semanticRelevance, emotionalRelevance,
                                 baseLevelActivation, temporal/semantic/emotionalSpreadActivation,
                                 retrievalActivation, retrievalLatency }, ... ],
  "associativelyActivated": [ { id, summaries, emotionMap, linkedVia: [{sourceMemoryId, linkType, strength}] }, ... ]
}
```

