import random
import uuid
from fastapi import FastAPI, HTTPException

app = FastAPI()

# Our quest pool - the possible quests someone can receive.
QUESTS = [
    {"id": 1, "category": "social", "difficulty": "easy", "text": "Call someone you haven't spoken to in a while."},
    {"id": 2, "category": "reflective", "difficulty": "easy", "text": "Write down 3 things you're avoiding right now."},
    {"id": 3, "category": "physical", "difficulty": "medium", "text": "Take a 20-minute walk with no phone."},
    {"id": 4, "category": "creative", "difficulty": "easy", "text": "Doodle something for 5 minutes, no judging it."},
    {"id": 5, "category": "social", "difficulty": "hard", "text": "Tell someone something you appreciate about them, out loud."},
]

# This is our "memory" of quests that have been handed out.
quest_instances = {}

@app.get("/")
def read_root():
    return {"message": "Hello, quester!"}

@app.get("/quest/new")
def get_new_quest():
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

    return quest_instances[instance_id]

def _resolve_quest(instance_id: str, new_status: str):
    """Shared helper: mark a quest instance with a given final status."""
    if instance_id not in quest_instances:
        raise HTTPException(status_code=404, detail="Quest instance not found")

    instance = quest_instances[instance_id]

    if instance["status"] != "in_progress":
        raise HTTPException(status_code=400, detail=f"Quest is already '{instance['status']}'")

    instance["status"] = new_status
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