"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from threading import Lock
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    # Sports activities
    "Soccer Team": {
        "description": "Competitive soccer team practicing tactics and teamwork",
        "schedule": "Mondays and Thursdays, 4:00 PM - 6:00 PM",
        "max_participants": 18,
        "participants": ["liam@mergington.edu", "ava@mergington.edu"]
    },
    "Swimming Club": {
        "description": "Lap swimming, technique coaching, and interschool meets",
        "schedule": "Tuesdays and Fridays, 5:00 PM - 6:30 PM",
        "max_participants": 25,
        "participants": ["noah@mergington.edu", "mia@mergington.edu"]
    },
    # Artistic activities
    "Art Club": {
        "description": "Explore drawing, painting, and mixed media projects",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": ["isabella@mergington.edu", "lucas@mergington.edu"]
    },
    "Drama Club": {
        "description": "Acting workshops and school play productions",
        "schedule": "Thursdays, 4:00 PM - 6:00 PM",
        "max_participants": 30,
        "participants": ["charlotte@mergington.edu", "ethan@mergington.edu"]
    },
    # Intellectual activities
    "Debate Team": {
        "description": "Competitive debating and public speaking practice",
        "schedule": "Mondays, 4:00 PM - 5:30 PM",
        "max_participants": 16,
        "participants": ["amelia@mergington.edu", "jack@mergington.edu"]
    },
    "Science Club": {
        "description": "Hands-on experiments, competitions, and science fairs",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 24,
        "participants": ["william@mergington.edu", "harper@mergington.edu"]
    }
}
activities_lock = Lock()

@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

     # Normalize email for duplicate checking
    normalized_email = email.strip().lower()

    with activities_lock:
        existing = {p.strip().lower() for p in activity.get("participants", [])}
        if normalized_email in existing:
            raise HTTPException(status_code=400, detail="Student is already signed up")

        # Add student (store the trimmed original email)
        activity.setdefault("participants", []).append(email.strip())

    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]

    normalized_email = email.strip().lower()

    with activities_lock:
        participants = activity.get("participants", [])
        # find index by case-insensitive match
        idx = None
        for i, p in enumerate(participants):
            if p.strip().lower() == normalized_email:
                idx = i
                break

        if idx is None:
            raise HTTPException(status_code=404, detail="Student not found in activity")

        # remove the participant
        removed = participants.pop(idx)

    return {"message": f"Unregistered {removed} from {activity_name}"}