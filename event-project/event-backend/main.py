from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from uuid import uuid4, UUID
from pymongo import MongoClient
from bson import Binary

app = FastAPI()

class Event(BaseModel):
    title: str
    description: str
    date: str

class EventInDB(Event):
    id: UUID

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["event_management_system"]
collection = db["schedule"]

@app.post("/events/", response_model=EventInDB)
async def create_event(event: Event):
    event_id = uuid4()
    event_in_db = EventInDB(id=event_id, **event.dict())
    collection.insert_one({**event_in_db.dict(), "id": Binary.from_uuid(event_id)})
    return event_in_db

@app.get("/events/", response_model=List[EventInDB])
async def read_events():
    events = list(collection.find())
    return [
        EventInDB(
            **{
                **event,
                "id": UUID(bytes=event["id"])
            }
        )
        for event in events
    ]

@app.get("/events/{event_id}", response_model=EventInDB)
async def read_event(event_id: UUID):
    event = collection.find_one({"id": Binary.from_uuid(event_id)})
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return EventInDB(
        **{
            **event,
            "id": UUID(bytes=event["id"])
        }
    )

@app.put("/events/{event_id}", response_model=EventInDB)
async def update_event(event_id: UUID, event: Event):
    existing_event = collection.find_one({"id": Binary.from_uuid(event_id)})
    if existing_event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    updated_event = EventInDB(id=event_id, **event.dict())
    collection.update_one(
        {"id": Binary.from_uuid(event_id)}, 
        {"$set": {**updated_event.dict(), "id": Binary.from_uuid(event_id)}}
    )
    return updated_event

@app.delete("/events/{event_id}")
async def delete_event(event_id: UUID):
    result = collection.delete_one({"id": Binary.from_uuid(event_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event deleted successfully"}

