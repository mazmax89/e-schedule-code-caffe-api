from enum import unique
import os
import re

from pymongo import MongoClient
from bson import ObjectId

client = MongoClient(os.environ["MONGO_URI"])

db = client.get_default_database()
users = db.get_collection("users")
users.create_index("slug", unique=True)


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower())


for user in users.find():
    print(user["name"], slugify(user["name"]))
    users.update_one(
        {"_id": user["_id"]},
        {"$set": {"slug": slugify(user["name"])}},
    )