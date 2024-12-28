import os
from pymongo.mongo_client import MongoClient

MONGO_URL = os.getenv("MONGO_URL")
client = MongoClient(MONGO_URL)