import random
from faker import Faker
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

# Initialize Faker
fake = Faker()

# MongoDB connection details
mongo_uri = "mongodb+srv://105250334:password007%21%21@cluster0.6vqz8.mongodb.net/flutter"
client = MongoClient(mongo_uri)
db = client.get_database("flutter")
users_collection = db.users
occupations_collection = db.occupations

# Fetch occupations from the "occupations" collection
occupations_cursor = occupations_collection.find({}, {"Occupation": 1, "ANZSCO code": 1, "Industry": 1, "Type": 1})
occupations = list(occupations_cursor)

if not occupations:
    raise ValueError("No occupations found in the 'occupations' collection.")

# Generate 500 mock migrants
migrants = []
for _ in range(500):
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = f"{first_name.lower()}.{last_name.lower()}@{fake.free_email_domain()}"
    
    # Select a random occupation from the fetched list
    selected_occupation = random.choice(occupations)
    occupation_name = selected_occupation["Occupation"]
    anzsco_code = selected_occupation.get("ANZSCO code", "N/A")
    industry = selected_occupation.get("Industry", "N/A")
    occupation_type = selected_occupation.get("Type", "N/A")

    migrant = {
        "_id": ObjectId(),
        "email": email,
        "password_hash": "scrypt:32768:8:1$eWpTWPBeJvLxuQCH$4a4a82396cf5e1995b8ae86eb124a011b3dfdad197d6447991055d58df034d4fee3503beafae63ededf51815fafd974dfae0b7b290a9e07ef2df7410e9326e77",  # Use a fixed hash for simplicity
        "role": "Migrant",
        "current_country": fake.country().lower(),
        "dob": fake.date_of_birth(minimum_age=18, maximum_age=60).strftime("%Y-%m-%d"),
        "first_name": first_name,
        "last_name": last_name,
        "nationality": fake.country().lower(),
        "occupation": occupation_name,
        "anzsco_code": anzsco_code,
        "industry": industry,
        "occupation_type": occupation_type,
        "profile_complete": random.choice([True, False])
    }
    
    migrants.append(migrant)

# Insert the generated migrants into the MongoDB collection
result = users_collection.insert_many(migrants)
print(f"Inserted {len(result.inserted_ids)} migrant records into the database.")
