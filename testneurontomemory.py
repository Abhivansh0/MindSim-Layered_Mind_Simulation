from dataclasses import dataclass
from datetime import datetime
from collections import deque
from typing import Dict, List, Optional
import uuid
import ast
import chromadb


# ─────────────────────────────────────────────────────────────────────────────
# MEMORY DATACLASS
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Memory:
    id: str                              # unique id for this memory (uuid)
    stimulus_summary: str                # short text of what triggered the memory
    response_summary: str                # short text of how the mind responded
    stimulus_vector: List[float]         # embedding of the stimulus, used for similarity search
    emotion_map: Dict[str, float]        # snapshot of all emotion values at the moment of creation
    initial_emotional_weight: float     # frozen at creation, never changes
    strength: float                     # starts equal to initial_emotional_weight, decays over time
    timestamp: datetime                  # when the memory was created
    recall_count: int = 0                # how many times this memory has been retrieved
    last_recalled: Optional[datetime] = None  # last time it was retrieved, used for decay timing


# ─────────────────────────────────────────────────────────────────────────────
# MEMORY LAYER
# ─────────────────────────────────────────────────────────────────────────────

class MemoryLayer:

    # --- Emotional weight formula ---
    ACTIVE_EMOTION_THRESHOLD = 0.30     # emotions below this don't count toward the active average
    COMPOUND_BONUS           = 0.08     # weight added per active compound emotion (complexity)
    COMPLEXITY_CAP           = 0.20     # max total bonus from compound emotions

    # --- Retrieval ---
    ACTIVE_SIMILARITY_THRESHOLD   = 0.40   # min raw similarity to surface an active memory
    DORMANT_SIMILARITY_THRESHOLD  = 0.60   # dormant memories need a stronger match to surface
    ARCHIVED_SIMILARITY_THRESHOLD = 0.87   # archived memories need an even stronger match
    RECALL_BOOST_RATE             = 0.15   # how much strength is restored per recall (diminishing returns)
    TOP_K                         = 5      # default number of memories returned per retrieval

    # --- Decay ---
    BASE_DECAY_RATE  = 0.005     # base daily decay rate before emotional weight adjustment
    DECAY_THRESHOLD  = 0.30      # strength below this triggers a move out of active
    DORMANT_CUTOFF   = 0.70      # initial_emotional_weight at/above this routes to dormant, else archived

    # --- Context window ---
    MAX_CONTEXT_WINDOW = 5     # how many recent stimulus/response pairs are kept in short-term context

    # sets up the connection to ChromaDB and creates/loads the three tier collections
    def __init__(self, mind_state):
        self.mind_state = mind_state                                   # reference to the shared mind state object
        self.context_window = deque(maxlen=self.MAX_CONTEXT_WINDOW)    # rolling buffer of recent interactions

        self.chroma_client = chromadb.HttpClient(host="localhost", port=8000)  # connect to local ChromaDB server

        # three separate collections — one per tier
        self.active_collection   = self.chroma_client.get_or_create_collection(
            name="mindsim_active",
            metadata={"hnsw:space": "cosine"}   # must set cosine explicitly, ChromaDB defaults to squared L2
        )
        self.dormant_collection  = self.chroma_client.get_or_create_collection(
            name="mindsim_dormant",
            metadata={"hnsw:space": "cosine"}
        )
        self.archived_collection = self.chroma_client.get_or_create_collection(
            name="mindsim_archived",
            metadata={"hnsw:space": "cosine"}
        )

        print(
            f"ChromaDB Ready | "
            f"Active: {self.active_collection.count()} | "
            f"Dormant: {self.dormant_collection.count()} | "
            f"Archived: {self.archived_collection.count()}"
        )


    # ─────────────────────────────────────────────────────────────────────────
    # STORAGE SUBMODULE
    # ─────────────────────────────────────────────────────────────────────────

    def create_memory(
        self,
        stimulus_summary: str,
        response_summary: str,
    ) -> Memory:

        stimulus_vector = self.mind_state.stimulus_vector.tolist()   # pull current stimulus embedding from mind state
        emotion_snapshot = self._snapshot_emotion_map()               # capture emotions as they are right now
        initial_emotional_weight = self._calculate_emotional_weight() # compute how emotionally significant this moment is

        memory = Memory(
            id=str(uuid.uuid4()),                       # generate a new unique id
            stimulus_summary=stimulus_summary,
            response_summary=response_summary,
            stimulus_vector=stimulus_vector,
            emotion_map=emotion_snapshot,
            initial_emotional_weight=initial_emotional_weight,
            strength=initial_emotional_weight,           # strength starts equal to the initial weight
            timestamp=datetime.now(),
        )

        # all memories are born in the active collection
        self.active_collection.add(
            ids=[memory.id],
            embeddings=[memory.stimulus_vector],
            metadatas=[{
                "stimulus_summary":         memory.stimulus_summary,
                "response_summary":         memory.response_summary,
                "initial_emotional_weight": memory.initial_emotional_weight,
                "strength":                 memory.strength,
                "recall_count":             memory.recall_count,
                "last_recalled":            "",             # empty string means never recalled yet
                "timestamp":                str(memory.timestamp),   # ChromaDB metadata must be primitive types
                "emotion_map":              str(emotion_snapshot)    # stored as string, parsed back out with ast.literal_eval
            }]
        )

        print(
            f"Memory stored | "
            f"weight: {memory.initial_emotional_weight:.2f} | "
            f"'{memory.stimulus_summary}'"
        )

        return memory


    def update_context_window(self, stimulus: str, response: str):
        self.context_window.append({           # add newest interaction, oldest auto-drops (deque maxlen)
            "stimulus":  stimulus,
            "response":  response,
            "timestamp": datetime.now()
        })


    def _snapshot_emotion_map(self) -> Dict[str, float]:
        snapshot = {}
        for emotion, data in self.mind_state.emotional_state["base"].items():
            snapshot[emotion] = data["value"]              # pull just the value, drop any extra metadata
        for compound, value in self.mind_state.emotional_state["compounds"].items():
            snapshot[compound] = value                      # compounds are stored as plain values already
        return snapshot


    def _calculate_emotional_weight(self) -> float:
        base_values = [
            data["value"]
            for data in self.mind_state.emotional_state["base"].values()
        ]
        compound_values = list(
            self.mind_state.emotional_state["compounds"].values()
        )
        all_values = base_values + compound_values

        if not all_values:
            return 0.0                                       # no emotional data at all -> neutral weight

        peak = max(all_values)                                                     # strongest single emotion firing
        active_emotions = [v for v in base_values if v >= self.ACTIVE_EMOTION_THRESHOLD]  # only count emotions that are actually "on"
        active_average = (sum(active_emotions) / len(active_emotions)) if active_emotions else 0.0
        complexity = min(len(compound_values) * self.COMPOUND_BONUS, self.COMPLEXITY_CAP)  # more compounds firing = more complex feeling

        emotional_weight = (peak * 0.65) + (active_average * 0.25) + complexity     
        return max(0.0, min(emotional_weight, 1.0))          # clamp to [0, 1]


    # ─────────────────────────────────────────────────────────────────────────
    # RETRIEVAL SUBMODULE
    # ─────────────────────────────────────────────────────────────────────────

    def retrieve_memories(self, stimulus_vector, top_k=None):
        if top_k is None:
            top_k = self.TOP_K

        stimulus_vector = stimulus_vector.tolist() if hasattr(stimulus_vector, "tolist") else stimulus_vector  # accept numpy array or plain list

        candidates = []

        # all three collections queried every time
        # what makes archived hard to surface is the 0.87 threshold gate, not whether we search it
        for collection, threshold in [
            (self.active_collection,   self.ACTIVE_SIMILARITY_THRESHOLD),
            (self.dormant_collection,  self.DORMANT_SIMILARITY_THRESHOLD),
            (self.archived_collection, self.ARCHIVED_SIMILARITY_THRESHOLD),
        ]:
            if collection.count() == 0:
                continue                                      # skip empty collections, nothing to query

            results = collection.query(
                query_embeddings=[stimulus_vector],
                n_results=min(top_k * 2, collection.count())  # over-fetch so threshold filtering still leaves enough candidates
            )

            candidates += self._filter_by_threshold(results, threshold, collection.name)

        # rank by similarity * strength, take top k
        candidates.sort(key=lambda c: c["similarity"] * c["metadata"]["strength"], reverse=True)  # strong-but-distant can lose to weak-but-close, by design
        top_memories = candidates[:top_k]

        for memory in top_memories:
            self._update_recall_metadata(memory)              # recalling a memory boosts its strength and logs the recall

        return top_memories


    def _filter_by_threshold(self, query_result, threshold: float, collection_name: str):
        passed = []

        ids       = query_result["ids"][0]
        metadatas = query_result["metadatas"][0]
        distances = query_result["distances"][0]

        for id_, metadata, distance in zip(ids, metadatas, distances):
            similarity = 1 - distance                          # cosine distance -> similarity
            print(f"    [debug] '{metadata['stimulus_summary']}' | collection={collection_name} | similarity={similarity:.4f} | threshold={threshold}")
            if similarity >= threshold:
                passed.append({
                    "id":              id_,
                    "metadata":        metadata,
                    "similarity":      similarity,
                    "collection_name": collection_name
                })

        return passed


    def _get_collection_by_name(self, collection_name: str):
        if collection_name == "mindsim_active":         # small helper so callers can go from name -> collection object
            return self.active_collection
        elif collection_name == "mindsim_dormant":
            return self.dormant_collection
        elif collection_name == "mindsim_archived":
            return self.archived_collection


#called whenever a memory is successfully retrieved
#Increase recall count
#Increase strength
#Update last recalled
#(Currently) move dormant → active
    def _update_recall_metadata(self, memory):
        metadata = memory["metadata"]
        collection = self._get_collection_by_name(memory["collection_name"])

        new_recall_count = metadata["recall_count"] + 1
        current_strength = metadata["strength"]
        new_strength = current_strength + (1 - current_strength) * self.RECALL_BOOST_RATE  # diminishing returns, mirrors decay formula

        updated_metadata = {
            **metadata,
            "recall_count": new_recall_count,
            "strength":     new_strength,
            "last_recalled": str(datetime.now())
        }

        # dormant memory recalled -> move it to active collection
        if memory["collection_name"] == "mindsim_dormant":
            self.active_collection.add(                        # copy into active first...
                ids=[memory["id"]],
                embeddings=[self.dormant_collection.get(
                    ids=[memory["id"]], include=["embeddings"]
                )["embeddings"][0]],
                metadatas=[updated_metadata]
            )
            self.dormant_collection.delete(ids=[memory["id"]])  # ...then remove from dormant, so we never lose it mid-move
            memory["collection_name"] = "mindsim_active"
            print(f"Memory revived to Active: '{metadata['stimulus_summary']}'")
        else:
            collection.update(ids=[memory["id"]], metadatas=[updated_metadata])  # active/archived just update in place

        memory["metadata"] = updated_metadata



    # ─────────────────────────────────────────────────────────────────────────
    # DECAY LOOP
    # ─────────────────────────────────────────────────────────────────────────

    def run_decay(self):
        all_active = self.active_collection.get()   # pull every memory currently in the active tier

        for id_, metadata in zip(all_active["ids"], all_active["metadatas"]):
            reference_time_str = metadata["last_recalled"] if metadata["last_recalled"] else metadata["timestamp"]  # decay from last recall, or creation if never recalled
            days_since_recall = (datetime.now() - datetime.fromisoformat(reference_time_str)).days

            effective_decay_rate = self.BASE_DECAY_RATE * (1 - metadata["initial_emotional_weight"])  # emotionally heavier memories decay slower
            new_strength = metadata["strength"] * ((1 - effective_decay_rate) ** days_since_recall)     # exponential-style decay
            new_strength = max(0.0, new_strength)

            if new_strength < self.DECAY_THRESHOLD:
                # move to the right collection based on initial emotional weight
                destination = (
                    self.dormant_collection
                    if metadata["initial_emotional_weight"] >= self.DORMANT_CUTOFF
                    else self.archived_collection
                )
                destination_name = (
                    "dormant" if metadata["initial_emotional_weight"] >= self.DORMANT_CUTOFF
                    else "archived"
                )

                updated_metadata = {**metadata, "strength": new_strength}

                # add to destination first, delete from active only after success
                embedding = self.active_collection.get(
                    ids=[id_], include=["embeddings"]
                )["embeddings"][0]

                destination.add(                                # copy into destination tier...
                    ids=[id_],
                    embeddings=[embedding],
                    metadatas=[updated_metadata]
                )
                self.active_collection.delete(ids=[id_])         # ...then remove from active, so it's never in two places or nowhere

                print(f"Memory -> {destination_name}: '{metadata['stimulus_summary']}' (strength={new_strength:.3f})")

            else:
                updated_metadata = {**metadata, "strength": new_strength}
                self.active_collection.update(ids=[id_], metadatas=[updated_metadata])  # still active, just save the decayed strength