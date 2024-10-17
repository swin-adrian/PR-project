import csv
from pymongo import MongoClient
from datetime import datetime

# MongoDB connection details
MONGO_URI = "mongodb+srv://105250334:password007!!@cluster0.6vqz8.mongodb.net/flutter"
DATABASE_NAME = "flutter"              # Use 'flutter' as the database name
COLLECTION_NAME = "courses"            # Replace with your collection name

# Function to parse the date from the CSV
def parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Read the CSV file and insert each row as a document in MongoDB
csv_file_path = "./data/Updated_Courses_with_Dates.csv"

with open(csv_file_path, mode='r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        # Convert data types as needed
        row['Cost'] = float(row['Cost'])
        row['CreatedAt'] = parse_date(row['CreatedAt'])

        # Insert into MongoDB
        collection.insert_one(row)

print("Data insertion completed successfully.")
