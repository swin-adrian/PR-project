import random
from pymongo import MongoClient
import math

# MongoDB connection details
mongo_uri = "mongodb+srv://105250334:password007%21%21@cluster0.6vqz8.mongodb.net/flutter"
client = MongoClient(mongo_uri)
db = client.get_database("flutter")
users_collection = db["users"]

# Define possible genders with corresponding probabilities
genders = ["Male", "Female", "Non-binary"]
weights = [0.475, 0.475, 0.05]  # 47.5% Male, 47.5% Female, 5% Non-binary

# Find all migrants without a gender field
migrants_without_gender = users_collection.find({"role": "Migrant", "gender": {"$exists": False}})

# Update each migrant with a randomly assigned gender based on the weights
for migrant in migrants_without_gender:
    # Randomly select a gender with the specified weights
    gender = random.choices(genders, weights)[0]
    
    # Update the document to include the gender field
    users_collection.update_one(
        {"_id": migrant["_id"]},
        {"$set": {"gender": gender}}
    )

print("Gender assignment completed successfully.")