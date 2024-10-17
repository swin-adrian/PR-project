import random
from pymongo import MongoClient
from bson import ObjectId

# MongoDB connection details
mongo_uri = "mongodb+srv://105250334:password007%21%21@cluster0.6vqz8.mongodb.net/flutter"
client = MongoClient(mongo_uri)
db = client.get_database("flutter")
users_collection = db.users
connections_collection = db.connections

# Agent ID
agent_id = ObjectId("670f73a303e5046db4db64a4")

# Step 1: Get 200 random migrant IDs from the database
migrants_cursor = users_collection.aggregate([
    {"$match": {"role": "Migrant"}},  # Match only users with role "Migrant"
    {"$sample": {"size": 200}}  # Randomly select 200 migrants
])
migrant_ids = [migrant["_id"] for migrant in migrants_cursor]

# Step 2: Create or update the "connections" document for the specified agent
# Check if a connection document for the agent already exists
existing_connection = connections_collection.find_one({"agentid": agent_id})

if existing_connection:
    # If the document exists, update it by adding the new migrant IDs
    connections_collection.update_one(
        {"agentid": agent_id},
        {"$addToSet": {"migrantids": {"$each": migrant_ids}}}
    )
else:
    # If no document exists, create a new one
    connection_document = {
        "agentid": agent_id,
        "migrantids": migrant_ids
    }
    connections_collection.insert_one(connection_document)

print(f"Paired 200 migrants with agent ID: {agent_id}")
