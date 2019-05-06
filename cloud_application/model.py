from uuid import uuid4
from hashlib import sha3_512
import pymongo
import os


db_url = "mongodb://localhost:27017/cloud"
client = pymongo.MongoClient(db_url)
db = client.get_database()

receivers_collection = db["receivers"]
users_collection = db["users"]


def register_user(username, password):

    hashed_password = _hash_password(password)

    if users_collection.find_one({"username": username}) is not None:
        return False

    users_collection.insert_one({"username": username, "password": hashed_password, "key": os.urandom(36).hex()})

    return True


def is_valid_user(username, password):

    hashed_password = _hash_password(password)
    return users_collection.find_one({"username": username, "password": hashed_password}) is not None


def change_user_password(username, old_password, new_password):

    hashed_old_password = _hash_password(old_password)
    hashed_new_password = _hash_password(new_password)

    result = users_collection.update_one({"username": username, "password": hashed_old_password}, {"$set": {"password": hashed_new_password}})

    return result.matched_count == 1


def get_user_visualisation_key(username):

    user = users_collection.find_one({"username": username})

    if user is None:
        return None

    return user["key"]


def create_receiver(email_address):

    email_object = {"id": uuid4(), "email": email_address}
    receivers_collection.insert_one({"id": email_object["id"], "email": email_object["email"]})

    return email_object


def receiver_email_exists(email_address):

    return receivers_collection.find_one({"email": email_address}) is not None


def get_receivers():

    return list(receivers_collection.find({}, {'_id': False}))


def get_receivers_emails():

    return [email_object["email"] for email_object in receivers_collection.find({}, {'_id': False})]


def get_receiver(index):

    return receivers_collection.find_one({"id": index}, {'_id': False})


def delete_receivers():

    receivers_collection.delete_many({})

    return []


def delete_receiver(email_object):

    receivers_collection.delete_one(email_object)


def _hash_password(password):

    return sha3_512(password.encode()).hexdigest()

