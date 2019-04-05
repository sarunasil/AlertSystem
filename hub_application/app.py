from flask import Flask, request, jsonify, abort
import os
import sys


app = Flask(__name__)

pipe = "/tmp/communication"
if not os.path.exists(pipe):
    os.mkfifo(pipe)

pipefile = os.open(pipe, os.O_WRONLY)

data = {
    "sensors": {},
    "ringers": {}
}


@app.route('/devices/sensors', methods=['GET', 'POST', 'DELETE'])
def sensors():

    if request.method == 'POST':
        body = request.json

        mac_addr, alias = validate_post_body(body)  # raises a 400 Bad request in case of an invalid body

        if alias in data["sensors"]:
            abort(409, "A sensor with that name was already registered.")

        data["sensors"][alias] = {"MAC": mac_addr, "alias": alias}

        os.write(pipefile, b"NOTIFY:SENSORS\n")

        return jsonify(data["sensors"][alias])

    elif request.method == 'GET':
        return jsonify(data["sensors"])

    elif request.method == 'DELETE':

        data["sensors"] = {}

        os.write(pipefile, b"NOTIFY:SENSORS\n")

        return jsonify(data["sensors"])


@app.route('/devices/ringers', methods=['GET', 'POST', 'DELETE'])
def ringers():
    if request.method == 'POST':
        body = request.json

        mac_addr, alias = validate_post_body(body)  # raises a 400 Bad request in case of an invalid body

        if alias in data["ringers"]:
            abort(409, "A ringer with that name was already registered.")

        data["ringers"][alias] = {"MAC": mac_addr, "alias": alias}

        os.write(pipefile, b"NOTIFY:RINGERS\n")

        return jsonify(data["ringers"][alias])

    elif request.method == 'GET':
        return jsonify(data["ringers"])

    elif request.method == 'DELETE':
        data["ringers"] = {}

        os.write(pipefile, b"NOTIFY:RINGERS\n")

        return jsonify(data["ringers"])


@app.route('/alerts', methods=['POST', 'DELETE'])
def alerts_management():

    global pipefile

    if request.method == 'POST':
        # read the body
        print("Sending to cloud")
        return jsonify({"msg": "Sent to cloud"})

    elif request.method == 'DELETE':
        print("Writing to pipe")
        os.write(pipefile, b"RESET\n")
        return jsonify({"msg": "Sent to BLE handler"})


def validate_post_body(body):

    if body is None:
        abort(400, "Expecting a JSON request body")

    if body.keys() != {"MAC", "alias"}:
        abort(400, "Expecting MAC address and alias in request body")

    mac_addr = body.get("MAC")
    if type(mac_addr) != str:
        abort(400, "Mac address must be a string value.")

    alias = body.get("alias")
    if type(alias) != str:
        abort(400, "Alias must be a string value.")

    return mac_addr, alias


if __name__ == "__main__":

    app.run(port=8080)
