from uuid import uuid4
import pymongo


db_url = "mongodb://localhost:27017/cloud"
client = pymongo.MongoClient(db_url)
db = client.get_database()

receivers_collection = db["receivers"]
users_collection = db["users"]


def is_valid_user(username, password):

    return users_collection.find_one({"username": username, "password": password}) is not None


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
