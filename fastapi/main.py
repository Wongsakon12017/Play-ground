from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pydantic import BaseModel
from bson.objectid import ObjectId

app = FastAPI()
client = MongoClient("mongodb://localhost:27017/")
db = client["votes"]
collection = db["votes"]

class Vote(BaseModel):
    name: str
    count: int

@app.get("/")
async def root():
    return {"message": "Hello world"}

# Create
@app.post("/votes/")
async def create_vote(vote: Vote):
    try:
        result = collection.insert_one(vote.dict())
        return {
            "id": str(result.inserted_id),
            "name": vote.name,
            "count": vote.count,
        }
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Read
@app.get("/votes/{vote_id}")
async def read_vote(vote_id: str):
    try:
        vote = collection.find_one({"_id": ObjectId(vote_id)})
        if vote:
            return {"id": str(vote["_id"]), "name": vote["name"], "count": vote["count"]}
        else:
            raise HTTPException(status_code=404, detail="Vote not found")
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Update
@app.put("/votes/{vote_id}")
async def update_vote(vote_id: str, vote: Vote):
    try:
        result = collection.update_one({"_id": ObjectId(vote_id)}, {"$set": vote.dict(exclude_unset=True)})
        if result.modified_count == 1:
            return {"id": vote_id, "name": vote.name, "count": vote.count}
        else:
            raise HTTPException(status_code=404, detail="Vote not found")
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
