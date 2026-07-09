"""
=========================================================================
MindSim Memory Layer - Complete Lifecycle Test
=========================================================================

Tests:
✓ Memory Creation
✓ Emotional Weight Calculation
✓ Permanent Memory Detection
✓ Active Collection Storage
✓ Retrieval
✓ Recall Boost
✓ Context Window
✓ Decay
✓ Active -> Dormant
✓ Active -> Archived
✓ Dormant -> Active Revival
✓ Archived Retrieval
✓ Final Collection Validation
=========================================================================
"""

from datetime import datetime, timedelta
import chromadb
import numpy as np
import traceback

from Brain.Memory_layer import MemoryLayer


# ============================================================
# COLORS
# ============================================================

GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"


passed = 0
failed = 0


def success(msg):
    global passed
    passed += 1
    print(f"{GREEN}[PASS]{RESET} {msg}")


def failure(msg):
    global failed
    failed += 1
    print(f"{RED}[FAIL]{RESET} {msg}")


def title(msg):
    print()
    print("=" * 70)
    print(CYAN + msg + RESET)
    print("=" * 70)


# ============================================================
# MOCK MIND STATE
# ============================================================

class MockMindState:

    def __init__(self):

        self.stimulus_vector = np.array(
            [0.10,0.30,0.20,0.40,0.50,0.60,0.25,0.35]
        )

        self.emotional_state = {

            "base": {

                "joy":{
                    "value":0.20
                },

                "fear":{
                    "value":0.15
                },

                "anger":{
                    "value":0.10
                },

                "sadness":{
                    "value":0.10
                }

            },

            "compounds":{

            }

        }


mind = MockMindState()

memory_layer = MemoryLayer(mind)
# ============================================================
# CLEAN DATABASE
# ============================================================

title("Cleaning Previous Test Memories")

for collection in [

    memory_layer.active_collection,
    memory_layer.dormant_collection,
    memory_layer.archived_collection

]:

    data = collection.get()

    if len(data["ids"]):

        collection.delete(ids=data["ids"])

print("Collections cleaned.")

print()

print(
    f"Active   : {memory_layer.active_collection.count()}"
)

print(
    f"Dormant  : {memory_layer.dormant_collection.count()}"
)

print(
    f"Archived : {memory_layer.archived_collection.count()}"
)


# ============================================================
# HELPERS
# ============================================================

def set_emotions(
    joy,
    fear,
    anger,
    sadness,
    compounds=None
):

    if compounds is None:
        compounds = {}

    mind.emotional_state["base"]["joy"]["value"] = joy
    mind.emotional_state["base"]["fear"]["value"] = fear
    mind.emotional_state["base"]["anger"]["value"] = anger
    mind.emotional_state["base"]["sadness"]["value"] = sadness

    mind.emotional_state["compounds"] = compounds


def make_vector(seed):

    np.random.seed(seed)

    mind.stimulus_vector = np.random.rand(8)


def age_memory(
    collection,
    memory_id,
    days
):

    memory = collection.get(ids=[memory_id])

    metadata = memory["metadatas"][0]

    metadata["timestamp"] = str(
        datetime.now() - timedelta(days=days)
    )

    metadata["last_recalled"] = ""

    collection.update(
        ids=[memory_id],
        metadatas=[metadata]
    )
    # ============================================================
# MEMORY CREATION TESTS
# ============================================================

title("Memory Creation Tests")

try:

    # --------------------------------------------------------
    # NORMAL MEMORY
    # --------------------------------------------------------

    set_emotions(
        joy=0.45,
        fear=0.10,
        anger=0.05,
        sadness=0.05
    )

    make_vector(1)

    active_memory = memory_layer.create_memory(
        stimulus_summary="User drank coffee before coding.",
        response_summary="System noticed increased focus."
    )

    if active_memory.strength > 0:
        success("Normal memory created.")
    else:
        failure("Normal memory has invalid strength.")

    if not active_memory.permanent:
        success("Normal memory correctly marked non-permanent.")
    else:
        failure("Normal memory incorrectly permanent.")

    # --------------------------------------------------------
    # HIGH EMOTION MEMORY
    # Will eventually decay into Dormant
    # --------------------------------------------------------

    set_emotions(
    joy=0.72,
    fear=0.65,
    anger=0.58,
    sadness=0.18,
    compounds={
        "nostalgia":0.42
    }
)

    make_vector(2)

    dormant_memory = memory_layer.create_memory(
        stimulus_summary="User won the hackathon.",
        response_summary="Celebrated with friends."
    )

    if dormant_memory.initial_emotional_weight >= 0.70:
        success("Dormant candidate has high emotional weight.")
    else:
        failure(
            f"Expected >=0.70 got {dormant_memory.initial_emotional_weight:.3f}"
        )

    # --------------------------------------------------------
    # LOW EMOTION MEMORY
    # Will eventually archive
    # --------------------------------------------------------

    set_emotions(
        joy=0.18,
        fear=0.10,
        anger=0.08,
        sadness=0.06
    )

    make_vector(3)

    archive_memory = memory_layer.create_memory(
        stimulus_summary="User looked outside the window.",
        response_summary="Nothing significant happened."
    )

    if archive_memory.initial_emotional_weight < 0.70:
        success("Archive candidate created.")
    else:
        failure("Archive candidate weight unexpectedly high.")

    # --------------------------------------------------------
    # PERMANENT MEMORY
    # --------------------------------------------------------

    set_emotions(
        joy=1.0,
        fear=1.0,
        anger=1.0,
        sadness=1.0,
        compounds={
            "love":1.0,
            "grief":1.0,
            "purpose":1.0
        }
    )

    make_vector(4)

    permanent_memory = memory_layer.create_memory(
        stimulus_summary="Birth of first child.",
        response_summary="Life changing experience."
    )

    if permanent_memory.permanent:
        success("Permanent memory detected correctly.")
    else:
        failure("Permanent memory NOT detected.")

except Exception:
    traceback.print_exc()
    failure("Memory creation crashed.")
    # ============================================================
# VERIFY STORAGE
# ============================================================

title("Storage Verification")

active_count = memory_layer.active_collection.count()

print(f"Active Collection Count : {active_count}")

if active_count == 4:
    success("All memories stored in Active collection.")
else:
    failure(f"Expected 4 memories. Found {active_count}.")

stored = memory_layer.active_collection.get()

ids = stored["ids"]

expected = {

    active_memory.id,
    dormant_memory.id,
    archive_memory.id,
    permanent_memory.id

}

if expected.issubset(set(ids)):
    success("All IDs present inside Chroma.")
else:
    failure("Missing IDs inside Active collection.")

print()

for metadata in stored["metadatas"]:

    print("---------------------------------------")
    print("Stimulus :", metadata["stimulus_summary"])
    print("Strength :", round(metadata["strength"],3))
    print("Initial  :", round(metadata["initial_emotional_weight"],3))
    print("Permanent:", metadata["permanent"])
    # ============================================================
# RETRIEVAL TESTS
# ============================================================

title("Retrieval Tests")

try:

    # Use the exact vector used to create the first memory
    query_vector = active_memory.stimulus_vector

    results = memory_layer.retrieve_memories(query_vector)

    if len(results) > 0:
        success(f"Retrieved {len(results)} memories.")
    else:
        failure("No memories retrieved.")

    print()

    for i, memory in enumerate(results):

        print(f"Result {i+1}")
        print("--------------------------------")

        print("Stimulus :", memory["stimulus_summary"])
        print("Response :", memory["response_summary"])
        print("Collection :", memory["collection"])
        print("Similarity :", round(memory["similarity"],3))
        print("Strength :", round(memory["strength"],3))
        print()

except Exception:

    traceback.print_exc()
    failure("Retrieval crashed.")
    # ============================================================
# VERIFY RECALL COUNT
# ============================================================

title("Recall Count Test")

stored = memory_layer.active_collection.get(
    ids=[active_memory.id]
)

metadata = stored["metadatas"][0]

print("Recall Count :", metadata["recall_count"])

if metadata["recall_count"] == 1:
    success("Recall count incremented.")
else:
    failure("Recall count incorrect.")
    # ============================================================
# VERIFY RECALL BOOST
# ============================================================

title("Recall Boost Test")

before_strength = active_memory.initial_emotional_weight

updated = memory_layer.active_collection.get(
    ids=[active_memory.id]
)

after_strength = updated["metadatas"][0]["strength"]

print("Before :", round(before_strength,3))
print("After  :", round(after_strength,3))

if after_strength > before_strength:
    success("Recall boost increased strength.")
else:
    failure("Recall boost failed.")
    # ============================================================
# MULTIPLE RECALL BOOSTS
# ============================================================

title("Repeated Recall Boost")

for _ in range(5):

    memory_layer.retrieve_memories(
        active_memory.stimulus_vector
    )

updated = memory_layer.active_collection.get(
    ids=[active_memory.id]
)

metadata = updated["metadatas"][0]

print()

print("Recall Count :", metadata["recall_count"])
print("Strength     :", round(metadata["strength"],3))

if metadata["recall_count"] >= 6:
    success("Multiple recalls tracked.")
else:
    failure("Recall counter incorrect.")

if metadata["strength"] > after_strength:
    success("Strength continues increasing.")
else:
    failure("Strength did not increase.")
    # ============================================================
# RANKING TEST
# ============================================================

title("Ranking Test")

results = memory_layer.retrieve_memories(
    active_memory.stimulus_vector,
    top_k=4
)

scores = []

for memory in results:

    score = memory["similarity"] * memory["strength"]

    scores.append(score)

    print(
        memory["stimulus_summary"],
        " Score =",
        round(score,4)
    )

correct = all(
    scores[i] >= scores[i+1]
    for i in range(len(scores)-1)
)

if correct:
    success("Ranking correctly sorted.")
else:
    failure("Ranking order incorrect.")
    # ============================================================
# ARTIFICIALLY AGE MEMORIES
# ============================================================

title("Artificial Memory Aging")

print("Aging memories by 400 days...")

age_memory(
    memory_layer.active_collection,
    active_memory.id,
    400
)

age_memory(
    memory_layer.active_collection,
    dormant_memory.id,
    400
)

age_memory(
    memory_layer.active_collection,
    archive_memory.id,
    400
)

age_memory(
    memory_layer.active_collection,
    permanent_memory.id,
    400
)

success("All timestamps modified.")
# ============================================================
# RUN DECAY
# ============================================================

title("Running Decay Engine")

try:

    memory_layer.run_decay()

    success("Decay completed.")

except Exception:

    traceback.print_exc()

    failure("Decay engine crashed.")
    # ============================================================
# COLLECTION COUNTS
# ============================================================

title("Collection Counts")

active_count = memory_layer.active_collection.count()
dormant_count = memory_layer.dormant_collection.count()
archived_count = memory_layer.archived_collection.count()

print(f"Active    : {active_count}")
print(f"Dormant   : {dormant_count}")
print(f"Archived  : {archived_count}")
# ============================================================
# VERIFY DORMANT MIGRATION
# ============================================================

title("Dormant Migration")

dormant_data = memory_layer.dormant_collection.get()

dormant_ids = dormant_data["ids"]

if dormant_memory.id in dormant_ids:

    success("High emotional memory moved to Dormant.")

else:

    failure("Dormant migration failed.")
    # ============================================================
# VERIFY ARCHIVED MIGRATION
# ============================================================

title("Archived Migration")

archived_data = memory_layer.archived_collection.get()

archived_ids = archived_data["ids"]

if archive_memory.id in archived_ids:

    success("Low emotional memory archived.")

else:

    failure("Archive migration failed.")
    # ============================================================
# VERIFY PERMANENT MEMORY
# ============================================================

title("Permanent Memory Check")

active_data = memory_layer.active_collection.get()

active_ids = active_data["ids"]

if permanent_memory.id in active_ids:

    success("Permanent memory remained Active.")

else:

    failure("Permanent memory should never decay.")
    # ============================================================
# VERIFY ACTIVE MEMORY REMOVED
# ============================================================

title("Active Collection Cleanup")

active_ids = memory_layer.active_collection.get()["ids"]

if active_memory.id not in active_ids:

    success("Normal memory removed from Active.")

else:

    failure("Expired memory still Active.")
    # ============================================================
# PRINT DORMANT METADATA
# ============================================================

title("Dormant Metadata")

for metadata in memory_layer.dormant_collection.get()["metadatas"]:

    print("------------------------------------")

    print("Stimulus :", metadata["stimulus_summary"])

    print("Strength :", round(metadata["strength"],4))

    print("Initial  :", round(metadata["initial_emotional_weight"],4))

    print("Permanent:", metadata["permanent"])
    # ============================================================
# PRINT ARCHIVED METADATA
# ============================================================

title("Archived Metadata")

for metadata in memory_layer.archived_collection.get()["metadatas"]:

    print("------------------------------------")

    print("Stimulus :", metadata["stimulus_summary"])

    print("Strength :", round(metadata["strength"],4))

    print("Initial  :", round(metadata["initial_emotional_weight"],4))
 # ============================================================
# STRENGTH VALIDATION
# ============================================================

title("Strength Validation")

# ---------- Dormant ----------

if memory_layer.dormant_collection.count() > 0:

    dormant_meta = memory_layer.dormant_collection.get(
        ids=[dormant_memory.id]
    )["metadatas"][0]

    if dormant_meta["strength"] < dormant_meta["initial_emotional_weight"]:
        success("Dormant strength decayed.")
    else:
        failure("Dormant strength did not decay.")

else:

    print("No dormant memories present.")
    print("Dormant validation skipped.")

# ---------- Archived ----------

if memory_layer.archived_collection.count() > 0:

    archived_meta = memory_layer.archived_collection.get(
        ids=[archive_memory.id]
    )["metadatas"][0]

    print()

    print("Initial :", archived_meta["initial_emotional_weight"])
    print("Strength:", archived_meta["strength"])

    success("Archived memory exists.")

else:

    failure("Archived memory missing.")
    # ============================================================
# DORMANT REVIVAL TEST
# ============================================================

title("Dormant Revival Test")

try:

    dormant_vector = dormant_memory.stimulus_vector

    results = memory_layer.retrieve_memories(
        dormant_vector
    )

    active_ids = memory_layer.active_collection.get()["ids"]

    dormant_ids = memory_layer.dormant_collection.get()["ids"]

    if dormant_memory.id in active_ids:

        success("Dormant memory revived to Active.")

    else:

        failure("Dormant memory did not revive.")

    if dormant_memory.id not in dormant_ids:

        success("Dormant collection cleaned.")

    else:

        failure("Dormant memory still exists.")

except Exception:

    traceback.print_exc()

    failure("Dormant revival crashed.")
    # ============================================================
# DORMANT REVIVAL TEST
# ============================================================

title("Dormant Revival Test")

try:

    dormant_vector = dormant_memory.stimulus_vector

    results = memory_layer.retrieve_memories(
        dormant_vector
    )

    active_ids = memory_layer.active_collection.get()["ids"]

    dormant_ids = memory_layer.dormant_collection.get()["ids"]

    if dormant_memory.id in active_ids:

        success("Dormant memory revived to Active.")

    else:

        failure("Dormant memory did not revive.")

    if dormant_memory.id not in dormant_ids:

        success("Dormant collection cleaned.")

    else:

        failure("Dormant memory still exists.")

except Exception:

    traceback.print_exc()

    failure("Dormant revival crashed.")
    # ============================================================
# VERIFY RECALL METADATA AFTER REVIVAL
# ============================================================

title("Revived Memory Metadata")

metadata = memory_layer.active_collection.get(
    ids=[dormant_memory.id]
)["metadatas"][0]

print()

print("Recall Count :", metadata["recall_count"])
print("Strength     :", round(metadata["strength"],3))
print("Last Recall  :", metadata["last_recalled"])

if metadata["recall_count"] >= 1:

    success("Recall count preserved.")

else:

    failure("Recall count incorrect.")

if metadata["strength"] > metadata["initial_emotional_weight"] * 0.25:

    success("Strength restored after recall.")

else:

    failure("Strength unexpectedly low.")
    # ============================================================
# ARCHIVED MEMORY RETRIEVAL
# ============================================================

title("Archived Retrieval Test")

try:

    archived_vector = archive_memory.stimulus_vector

    results = memory_layer.retrieve_memories(
        archived_vector,
        top_k=10
    )

    archived_found = False

    for memory in results:

        if memory["id"] == archive_memory.id:

            archived_found = True

            print()

            print("Retrieved Archived Memory")

            print("----------------------------")

            print("Stimulus :", memory["stimulus_summary"])
            print("Response :", memory["response_summary"])
            print("Collection :", memory["collection"])

            if memory["stimulus_summary"].endswith("..."):

                success("Archived summary degraded.")

            else:

                failure("Archived summary not degraded.")

            break

    if archived_found:

        success("Archived memory retrieved.")

    else:

        failure("Archived memory not returned.")

except Exception:

    traceback.print_exc()

    failure("Archived retrieval crashed.")
    # ============================================================
# FINAL COLLECTION STATUS
# ============================================================

title("Final Collection Status")

active = memory_layer.active_collection.count()
dormant = memory_layer.dormant_collection.count()
archived = memory_layer.archived_collection.count()

print()

print(f"Active   : {active}")
print(f"Dormant  : {dormant}")
print(f"Archived : {archived}")

print()

for name, collection in [

    ("ACTIVE", memory_layer.active_collection),
    ("DORMANT", memory_layer.dormant_collection),
    ("ARCHIVED", memory_layer.archived_collection)

]:

    print("---------------------------------------")

    print(name)

    print("---------------------------------------")

    data = collection.get()

    for meta in data["metadatas"]:

        print(
            meta["stimulus_summary"],
            "| Strength:",
            round(meta["strength"],3)
        )

    print()
    # ============================================================
# CLEANUP
# ============================================================

title("Cleaning Test Database")

for collection in [

    memory_layer.active_collection,
    memory_layer.dormant_collection,
    memory_layer.archived_collection

]:

    ids = collection.get()["ids"]

    if len(ids):

        collection.delete(ids=ids)

print()

print("Remaining Active   :", memory_layer.active_collection.count())
print("Remaining Dormant  :", memory_layer.dormant_collection.count())
print("Remaining Archived :", memory_layer.archived_collection.count())

if (

    memory_layer.active_collection.count() == 0
    and
    memory_layer.dormant_collection.count() == 0
    and
    memory_layer.archived_collection.count() == 0

):

    success("Database cleanup successful.")

else:

    failure("Cleanup incomplete.")
    # ============================================================
# FINAL REPORT
# ============================================================

title("FINAL TEST REPORT")

total = passed + failed

print()

print("=" * 70)

print(f"Total Tests : {total}")

print(f"{GREEN}Passed : {passed}{RESET}")

print(f"{RED}Failed : {failed}{RESET}")

print("=" * 70)

accuracy = (passed / total) * 100 if total else 0

print()

print(f"Success Rate : {accuracy:.2f}%")

print()

if failed == 0:

    print(GREEN)
    print("🎉 ALL MEMORY LIFECYCLE TESTS PASSED")
    print(RESET)

else:

    print(YELLOW)
    print("⚠ Some tests failed.")
    print("Review the logs above.")
    print(RESET)