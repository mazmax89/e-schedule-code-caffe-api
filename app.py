from datetime import datetime
import os
import sys 
from flask import Flask, request, url_for, jsonify
import pymongo
from pymongo.collection import Collection, ReturnDocument
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

sys.path.append(os.path.abspath("/home/el/foo4/stuff"))
from userAPI.model import User
from userAPI.objectid import PydanticObjectId

# Configure Flask & Flask-PyMongo:
app = Flask(__name__)
pymongo = MongoClient("mongodb+srv://")

# Get a reference to the recipes collection.
# Uses a type-hint, so that your IDE knows what's happening!
users: Collection = pymongo.db.users

def get_db():
    db = pymongo["user"]
    return db

@app.errorhandler(404)
def resource_not_found(e):
    """
    An error-handler to ensure that 404 errors are returned as JSON.
    """
    return jsonify(error=str(e)), 404


@app.errorhandler(DuplicateKeyError)
def resource_not_found(e):
    """
    An error-handler to ensure that MongoDB duplicate key errors are returned as JSON.
    """
    return jsonify(error=f"Duplicate key error."), 400

@app.route('/')
def ping_server():
    try:
        pymongo.admin.command('ismaster')
    except:
        return "Server not available! CodeCafe"
    return "Welcome to the e-schedule API."


@app.route("/user/", methods=["POST"])
def new_user():
    raw_user = request.get_json()
    raw_user["date_added"] = datetime.utcnow()

    user = User(**raw_user)
    insert_result = users.insert_one(user.to_bson())
    user.id = PydanticObjectId(str(insert_result.inserted_id))
    print(user)

    return user.to_json()

@app.route('/user')
def get_stored_users():
    db=""
    try:
        db = get_db()
        db.users.find()
        _users = db.users.find()
        users = [{"name": user["name"]} for user in _users]
        return jsonify({"users": users})
    except:
        pass
    finally:
        if type(db)==MongoClient:
            db.close()

if __name__=='__main__':
    app.run(host="0.0.0.0", port=80, debug=True)
