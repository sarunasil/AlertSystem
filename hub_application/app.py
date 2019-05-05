from flask import Flask, request, jsonify, abort
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import datetime
import os
import model
import requests


app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.environ["JWT_SECRET_KEY"]
jwt = JWTManager(app)
jwt_user = os.environ["JWT_USER"]
jwt_password = os.environ["JWT_PASSWORD"]

pipe = "/tmp/communication"
if not os.path.exists(pipe):
    os.mkfifo(pipe)

pipefile = os.open(pipe, os.O_WRONLY)


# stores the scanning data in memory
data = {
    "scanning": {
        "timestamp": 0,
        "result": None
    }
}


@app.route('/login', methods=['POST'])
def login():

    if request.json is None:
        abort(400, "Expecting JSON body.")

    if request.json.keys() != {"username", "password"}:
        abort(400, "Expecting JSON body with username and password.")

    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if username != jwt_user or password != jwt_password:
        return jsonify({"msg": "Authentication failure."}), 401

    access_token = create_access_token(identity=username)
    return jsonify({"token": access_token}), 200


@app.route('/devices/sensors', methods=['GET', 'POST', 'DELETE'])
@jwt_required
def sensors():

    return jsonify(handle_request_for_devices("sensor"))


@app.route('/devices/sensors/<alias>', methods=['POST', 'GET', 'DELETE'])
@jwt_required
def sensors_instance(alias):

    return jsonify(handle_request_for_device_instance("sensor", alias))


@app.route('/devices/ringers', methods=['GET', 'POST', 'DELETE'])
@jwt_required
def ringers():

    return jsonify(handle_request_for_devices("ringer"))


@app.route('/devices/ringers/<alias>', methods=['POST', 'GET', 'DELETE'])
@jwt_required
def ringers_instance(alias):

    return jsonify(handle_request_for_device_instance("ringer", alias))


@app.route('/alarms', methods=['POST', 'DELETE'])
@jwt_required
def alarms_management():

    global pipefile

    if request.method == 'POST':
        # read the body
        print("Received alarm data", request.json)
        print("Sending to cloud")

        # hub needs to authenticate first
        response = requests.post("http://3.8.68.131:8080/login", json={"username": jwt_user, "password": jwt_password})
        token = response.json()["token"]
        headers = {"Authorization": "Bearer {0}".format(token)}

        requests.post('http://3.8.68.131:8080/alarms', json={"msg": "Alarm has been triggered - {0}".format(request.json)}, headers=headers)

        return jsonify({"msg": "Sent to cloud"})

    elif request.method == 'DELETE':
        print("Writing to pipe")
        # check the url parameter, if ?measure=true is included in the URL, write a RESET_AND_MEASURE, otherwise write a RESET
        # default value is assumed to be false
        if request.args.get("measure", "false") == "true":
            print("Writing RESET_AND_MEASURE")
            os.write(pipefile, b"RESET_AND_MEASURE\n")
        else:
            print("WRITING RESET")
            os.write(pipefile, b"RESET\n")

        return jsonify({"msg": "Sent stop command to BLE handler"})


@app.route('/devices/scanning', methods=['POST', 'GET'])
@jwt_required
def scanning():

    global pipefile

    if request.method == 'POST':
        os.write(pipefile, b"SCAN\n")
        return jsonify({"msg": "Sent scan command to BLE handler"})
    elif request.method == 'GET':
        if data["scanning"]["result"] is not None:
            current_timestamp = datetime.datetime.now().timestamp()
            if current_timestamp - data["scanning"]["timestamp"] >= 120:  # 120 seconds have passed since last scanning was executed
                data["scanning"]["result"] = None
                return jsonify({"msg": "Stale scanning results, please send a POST request for scanning to be performed by the BLE handler"})
            return jsonify(data["scanning"]["result"])
        else:
            return jsonify({"msg": "No scanning data available, please send a POST request for scanning to be performed by the BLE handler"})


@app.route('/devices/scanning/results', methods=['POST'])
@jwt_required
def scanning_results_from_handler():

    if request.method == 'POST':

        body = request.json
        if body is None:
            abort(400, "Expecting JSON body.")

        data["scanning"]["result"] = body
        data["scanning"]["timestamp"] = int(datetime.datetime.now().timestamp())

        return jsonify({"msg": "Scanning results have been saved"})


def handle_request_for_devices(device_type):

    # device_type should be "ringers" or "sensors"

    if request.method == 'POST':
        body = request.json

        mac_addr, alias = validate_post_body(body)  # raises a 400 Bad request in case of an invalid body

        if getattr(model, "{0}_exists".format(device_type))(alias):
            abort(409, "A device with that name was already registered in {0}.".format(device_type))

        device_body = getattr(model, "add_{0}".format(device_type))(alias, mac_addr)
        print("NOTIFY:" + device_type.upper())
        os.write(pipefile, b"NOTIFY:" + device_type.upper().encode("utf-8") + b"\n")

        return device_body

    elif request.method == 'GET':

        return getattr(model, "get_{0}s".format(device_type))()

    elif request.method == 'DELETE':

        getattr(model, "delete_{0}s".format(device_type))()

        os.write(pipefile, b"NOTIFY:" + device_type.upper().encode("utf-8") + b"\n")

        return []


def handle_request_for_device_instance(device_type, alias):

    # device_type should be "ringers" or "sensors"

    if not getattr(model, "{0}_exists".format(device_type))(alias):
        abort(404, "A {0} device with that alias was not registered.".format(device_type))

    if request.method == 'POST':

        body = request.json
        if body is None or body.keys() != {"status"}:
            abort(400, "Expecting JSON body.")

        getattr(model, "update_{0}".format(device_type))(alias, body)

        return getattr(model, "get_{0}".format(device_type))(alias)

    elif request.method == 'GET':

        return getattr(model, "get_{0}".format(device_type))(alias)

    elif request.method == 'DELETE':

        to_delete = getattr(model, "get_{0}".format(device_type))(alias)
        getattr(model, "delete_{0}".format(device_type))(alias)
        return to_delete


def validate_post_body(body):

    if body is None:
        abort(400, "Expecting a JSON request body")

    if body.keys() != {"mac", "alias"}:
        abort(400, "Expecting mac address and alias in request body")

    mac_addr = body.get("mac")
    if type(mac_addr) != str:
        abort(400, "Mac address must be a string value.")

    alias = body.get("alias")
    if type(alias) != str:
        abort(400, "Alias must be a string value.")

    return mac_addr, alias


if __name__ == "__main__":

    app.run(host='0.0.0.0', port=8080)
