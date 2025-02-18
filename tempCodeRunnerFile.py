from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
import threading
import os

# Initialize Flask app
app = Flask(__name__)

# MongoDB connection for Flask
MONGO_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGO_URI)
db = client.HR  # Replace with your database name
collection = db.candidate  # Replace with your collection name

# Function to convert MongoDB document
def convert_mongo_document(doc):
    doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
    return doc

# Route to create item
@app.route('/items/', methods=['POST'])
def create_item():
    try:
        item_data = request.get_json()  # Get data from the request
        item = {
            "name": item_data.get("name"),
            "phone_no": item_data.get("phone_no"),
            "email": item_data.get("email"),
            "chat": item_data.get("chat")
        }
        result = collection.insert_one(item)
        inserted_item = collection.find_one({"_id": result.inserted_id})
        if inserted_item:
            return jsonify({"id": str(result.inserted_id), "message": "Item inserted successfully"}), 201
        else:
            return jsonify({"message": "Failed to insert item"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Route to get data
@app.route('/data', methods=['GET'])
def get_data():
    try:
        candidate_data = list(collection.find())  # Fetch all documents as a list
        if candidate_data:
            return jsonify({
                "message": "Candidate Data retrieved successfully",
                "data": [convert_mongo_document(doc) for doc in candidate_data]  # Convert each document
            }), 200
        else:
            return jsonify({"message": "No data found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Function to run the Flask app in a separate thread
def run_flask():
    app.run(debug=True, use_reloader=False, port=5000)  # Flask on port 5000

# Main function to run Flask
if __name__ == "__main__":
    app.run(debug=True)
