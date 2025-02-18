from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import List, Dict
import os
# Initialize FastAPI app
app = FastAPI()


# MongoDB connection
MONGO_URI = os.getenv("MONGODB_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client.HR  # Replace with your database name
collection = db.candidate  # Replace with your collection name


# Define Pydantic model for data validation
class Item(BaseModel):
    name: str
    phone_no: str
    email: str
    chat: List[Dict[str, str]]
    
    
@app.post("/items/")
async def create_item(item: Item):
    new_item = await collection.insert_one(item.dict())
    inserted_item = await collection.find_one({"_id": new_item.inserted_id})
    if inserted_item:
        return {"id": str(new_item.inserted_id), "message": "Item inserted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to insert item")




# For get all the data
def convert_mongo_document(doc):
    doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
    return doc

@app.get("/data")
async def get_data():
    candidate_data = await collection.find().to_list(None)  # Fetch all documents as a list
    if candidate_data:
        return {
            "message": "Candidate Data retrieved successfully",
            "data": [convert_mongo_document(doc) for doc in candidate_data]  # Convert each document
        }
    else:
        raise HTTPException(status_code=404, detail="No data found")