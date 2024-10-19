import random
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson.objectid import ObjectId

# MongoDB connection details
mongo_uri = "mongodb+srv://105250334:password007%21%21@cluster0.6vqz8.mongodb.net/flutter"
client = MongoClient(mongo_uri)
db = client.get_database("flutter")

# Collections
users_collection = db["users"]
connections_collection = db["connections"]
courses_collection = db["courses"]
recommendations_collection = db["recommendations"]

# Fetch all agents
agents = list(users_collection.find({"role": "Agent"}))

# Fetch all course IDs
course_ids = [course["_id"] for course in courses_collection.find()]

if not course_ids:
    raise ValueError("No courses found to recommend.")

# Date range: October 1st to October 19th, 2024
start_date = datetime(2024, 10, 1)
end_date = datetime(2024, 10, 19)

def random_date_in_october():
    """Generate a random datetime between 1st and 19th October, 2024."""
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    random_time = timedelta(
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59)
    )
    return start_date + timedelta(days=random_days) + random_time

# Loop through each agent
for agent in agents:
    agent_id = agent["_id"]

    # Fetch the migrants managed by this agent
    connection = connections_collection.find_one({"agentid": ObjectId(agent_id)})
    if not connection or "migrantids" not in connection:
        continue

    migrant_ids = connection["migrantids"]

    # Loop through each migrant managed by this agent
    for migrant_id in migrant_ids:
        # Randomly select 1 to 3 courses for recommendation
        num_courses = random.randint(1, 3)
        selected_courses = random.sample(course_ids, num_courses)

        # Recommend each course
        for course_id in selected_courses:
            # Generate random recommendation date and feedback
            recommended_at = random_date_in_october()
            feedback = random.choice([
                "Hey, you should take this course.",
                "This course seems to be a great fit for you.",
                "Highly recommend you take this course!",
                "Consider enrolling in this course, it can boost your PR chances."
            ])

            # Prepare recommendation document
            recommendation_doc = {
                "agent_id": ObjectId(agent_id),
                "migrant_id": ObjectId(migrant_id),
                "course_id": ObjectId(course_id),
                "feedback": feedback,
                "recommended_at": recommended_at
            }

            # Insert the recommendation into the recommendations collection
            recommendations_collection.insert_one(recommendation_doc)

print("Course recommendations added for all agents and their migrants.")
