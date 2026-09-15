import random
import time
import uuid
from fastapi import FastAPI, HTTPException, Response
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI()

# ── Quest pool ──────────────────────────────────────────────
QUESTS = [
    {"id": 1, "category": "social", "difficulty": "easy", "text": "Call someone you haven't spoken to in a while."},
    {"id": 2, "category": "reflective", "difficulty": "easy", "text": "Write down 3 things you're avoiding right now."},
    {"id": 3, "category": "physical", "difficulty": "medium", "text": "Take a 20-minute walk with no phone."},
    {"id": 4, "category": "creative", "difficulty": "easy", "text": "Doodle something for 5 minutes, no judging it."},
    {"id": 5, "category": "social", "difficulty": "hard", "text": "Tell someone something you appreciate about them, out loud."},
]

quest_instances = {}

# ── Metrics ─────────────────────────────────────────────────
# COUNTER: something that only ever goes up.
quests_generated_total = Counter(
    "quests_generated_total",
    "Total number of quests generated",
    ["category"]
)

quests_completed_total = Counter(
    "quests_completed_total",
    "Total number of quests completed",
    ["category", "difficulty"]
)

quests_skipped_total = Counter(
    "quests_skipped_total",
    "Total number of quests skipped",
    ["category"]
)

quests_abandoned_total = Counter(
    "quests_abandoned_total",
    "Total number of quests abandoned",
    ["category"]
)

# GAUGE: something that goes up AND down.
quests_in_progress = Gauge(
    "quests_in_progress",
    "Number of quests currently in progress",
    ["category"]
)

# HISTOGRAM: measures how long something takes, sorted into buckets.
quest_generation_latency_seconds = Histogram(
    "quest_generation_latency_seconds",
    "Time taken to generate a new quest"
)

# ── Endpoints ───────────────────────────────────────────────
@app.get("/")
def read_root():
    return {"message": "Hello, quester!"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/quest/new")
def get_new_quest():
    start_time = time.time()  # mark when we started, so we can measure duration

    quest = random.choice(QUESTS)
    instance_id = str(uuid.uuid4())

    quest_instances[instance_id] = {
        "instance_id": instance_id,
        "quest_id": quest["id"],
        "category": quest["category"],
        "difficulty": quest["difficulty"],
        "text": quest["text"],
        "status": "in_progress",
    }

    # Update metrics
    quests_generated_total.labels(category=quest["category"]).inc()
    quests_in_progress.labels(category=quest["category"]).inc()

    duration = time.time() - start_time
    quest_generation_latency_seconds.observe(duration)

    return quest_instances[instance_id]

def _resolve_quest(instance_id: str, new_status: str):
    if instance_id not in quest_instances:
        raise HTTPException(status_code=404, detail="Quest instance not found")

    instance = quest_instances[instance_id]

    if instance["status"] != "in_progress":
        raise HTTPException(status_code=400, detail=f"Quest is already '{instance['status']}'")

    instance["status"] = new_status
    category = instance["category"]
    difficulty = instance["difficulty"]

    # This quest is no longer "in progress", so the gauge goes DOWN.
    quests_in_progress.labels(category=category).dec()

    # And the right counter goes UP.
    if new_status == "completed":
        quests_completed_total.labels(category=category, difficulty=difficulty).inc()
    elif new_status == "skipped":
        quests_skipped_total.labels(category=category).inc()
    elif new_status == "abandoned":
        quests_abandoned_total.labels(category=category).inc()

    return instance

@app.post("/quest/{instance_id}/complete")
def complete_quest(instance_id: str):
    return _resolve_quest(instance_id, "completed")

@app.post("/quest/{instance_id}/skip")
def skip_quest(instance_id: str):
    return _resolve_quest(instance_id, "skipped")

@app.post("/quest/{instance_id}/abandon")
def abandon_quest(instance_id: str):
    return _resolve_quest(instance_id, "abandoned")

@app.get("/quest/status")
def quest_status():
    return list(quest_instances.values())