from pymongo import MongoClient
import os

def get_database():
    mongo_uri = os.getenv('MONGO_URI')
    client = MongoClient(mongo_uri)
    db = client.get_default_database()
    return db


# from pymongo import MongoClient
# import os
# from dotenv import load_dotenv

# load_dotenv()

# # Retrieve MongoDB URI from environment variables
# mongo_uri = os.getenv("MONGO_URI")

# # Connect to MongoDB Atlas
# client = MongoClient(mongo_uri)
# db = client.get_database()
# collection = db['collection_flask']
