import pandas as pd
from pymongo import MongoClient

# Replace <username>, <password>, and <cluster-url> with your credentials and cluster URL
client = MongoClient("mongodb+srv://105250334:password007%21%21@cluster0.6vqz8.mongodb.net/fluttery")
db = client['flutter']
collection = db['occupations']

# Load CSV file into pandas DataFrame
df = pd.read_csv('./data/Occupation_list.csv')

# Convert DataFrame to dictionary records and insert into MongoDB Atlas
data = df.to_dict(orient='records')
collection.insert_many(data)

print("Data inserted successfully into MongoDB Atlas!")