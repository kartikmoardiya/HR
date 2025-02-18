from fastapi import FastAPI, HTTPException
from flask import Flask
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import List, Dict
import os
import threading
import uvicorn

# Initialize FastAPI app
fastapi_app = FastAPI()

# Initialize Flask app
flask_app = Flask(__name__)

# MongoDB connection for FastAPI
MONGO_URI = os.getenv("MONGODB_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client.HR  # Replace with your database name
collection = db.candidate  # Replace with your collection name

# Define Pydantic model for data validation in FastAPI
class Item(BaseModel):
    name: str
    phone_no: str
    email: str
    chat: List[Dict[str, str]]

# FastAPI route to create item
@fastapi_app.post("/items/")
async def create_item(item: Item):
    new_item = await collection.insert_one(item.dict())
    inserted_item = await collection.find_one({"_id": new_item.inserted_id})
    if inserted_item:
        return {"id": str(new_item.inserted_id), "message": "Item inserted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to insert item")

# FastAPI route to get data
def convert_mongo_document(doc):
    doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
    return doc

@fastapi_app.get("/data")
async def get_data():
    candidate_data = await collection.find().to_list(None)  # Fetch all documents as a list
    if candidate_data:
        return {
            "message": "Candidate Data retrieved successfully",
            "data": [convert_mongo_document(doc) for doc in candidate_data]  # Convert each document
        }
    else:
        raise HTTPException(status_code=404, detail="No data found")


# Flask route to handle simple request
@flask_app.route('/')
def hello_world():
    return 'Hello from Flask!'

# Function to run the Flask app in a separate thread
def run_flask():
    flask_app.run(debug=True, use_reloader=False, port=5000)  # Flask on port 5000

# Main function to run both FastAPI and Flask
def main():
    # Start Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Run FastAPI with Uvicorn
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
