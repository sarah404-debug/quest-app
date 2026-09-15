import random
from fastapi import FastAPI

app = FastAPI()

# This is our "quest pool" — a simple list for now.
# Later we could move this into a database, but a list is fine to start.
QUESTS = [
    {"id": 1, "category": "social", "difficulty": "easy", "text": "Call someone you haven't spoken to in a while."},
    {"id": 2, "category": "reflective", "difficulty": "easy", "text": "Write down 3 things you're avoiding right now."},
    {"id": 3, "category": "physical", "difficulty": "medium", "text": "Take a 20-minute walk with no phone."},
    {"id": 4, "category": "creative", "difficulty": "easy", "text": "Doodle something for 5 minutes, no judging it."},
    {"id": 5, "category": "social", "difficulty": "hard", "text": "Tell someone something you appreciate about them, out loud."},
]

@app.get("/")
def read_root():
    return {"message": "Hello, quester!"}

@app.get("/quest/new")
def get_new_quest():
    quest = random.choice(QUESTS)
    return quest