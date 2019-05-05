import pymongo

db_url = "mongodb://localhost:27017/devices"
client = pymongo.MongoClient(db_url)
db = client.get_database()

sensors_collection = db["sensors"]

ringers_collection = db["ringers"]


# ---------------------------------------------------------------------------------------- #
def get_sensors():
    return list(sensors_collection.find({}, {'_id': False}))


def get_sensor(alias):
    return sensors_collection.find_one({"alias": alias}, {'_id': False})


def sensor_exists(alias):
    return get_sensor(alias) is not None


def add_sensor(alias, mac):
    sensor_body = {"mac": mac, "alias": alias, "status": "disconnected"}
    sensors_collection.insert_one(sensor_body)
    return {"mac": mac, "alias": alias, "status": "disconnected"}


def delete_sensors():
    sensors_collection.delete_many({})


def delete_sensor(alias):
    sensors_collection.delete_one({"alias": alias})


def update_sensor(alias, updated_fields):
    sensors_collection.update_one({"alias": alias}, {"$set": updated_fields})


# ---------------------------------------------------------------------------------------- #
def get_ringers():
    return list(ringers_collection.find({}, {'_id': False}))


def get_ringer(alias):
    return ringers_collection.find_one({"alias": alias}, {'_id': False})


def ringer_exists(alias):
    return get_ringer(alias) is not None


def add_ringer(alias, mac):
    ringer_body = {"mac": mac, "alias": alias, "status": "disconnected"}
    ringers_collection.insert_one(ringer_body)
    return {"mac": mac, "alias": alias, "status": "disconnected"}


def delete_ringers():
    ringers_collection.delete_many({})


def delete_ringer(alias):
    ringers_collection.delete_one({"alias": alias})


def update_ringer(alias, updated_fields):
    ringers_collection.update_one({"alias": alias}, {"$set": updated_fields})
