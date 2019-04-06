from flask import Flask, request, jsonify, abort
import os


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

    return jsonify(handle_request_for_devices("sensors"))


@app.route('/devices/sensors/<alias>', methods=['POST', 'GET', 'DELETE'])
def sensors_instance(alias):

    return jsonify(handle_request_for_device_instance("sensors", alias))


@app.route('/devices/ringers', methods=['GET', 'POST', 'DELETE'])
def ringers():

    return jsonify(handle_request_for_devices("ringers"))


@app.route('/devices/ringers/<alias>', methods=['POST', 'GET', 'DELETE'])
def ringers_instance(alias):

    return jsonify(handle_request_for_device_instance("ringers", alias))


@app.route('/alarms', methods=['POST', 'DELETE'])
def alarms_management():

    global pipefile

    if request.method == 'POST':
        # read the body
        print("Received alarm data", request.json)
        print("Sending to cloud")
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

        return jsonify({"msg": "Sent to BLE handler"})


def handle_request_for_devices(device_type):

    # device_type should be "ringers" or "sensors"

    if request.method == 'POST':
        body = request.json

        mac_addr, alias = validate_post_body(body)  # raises a 400 Bad request in case of an invalid body

        if alias in data[device_type]:
            abort(409, "A device with that name was already registered in {0}.".format(device_type))

        data[device_type][alias] = {"mac": mac_addr, "alias": alias, "status": "disconnected"}

        os.write(pipefile, b"NOTIFY:" + device_type.upper().encode("utf-8") + b"\n")

        return data[device_type][alias]

    elif request.method == 'GET':
        return data[device_type]

    elif request.method == 'DELETE':
        data[device_type] = {}

        os.write(pipefile, b"NOTIFY:" + device_type.upper().encode("utf-8") + b"\n")

        return data[device_type]


def handle_request_for_device_instance(device_type, alias):

    # device_type should be "ringers" or "sensors"

    if alias not in data[device_type]:
        abort(404, "A device with that name was not registered in {0}.".format(device_type))

    if request.method == 'POST':

        body = request.json
        if body is None or "status" not in body:
            abort(400, "Expecting JSON body.")

        data[device_type][alias]["status"] = body["status"]

        return data[device_type][alias]

    elif request.method == 'GET':

        return data[device_type][alias]

    elif request.method == 'DELETE':

        return data[device_type].pop(alias)


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

    app.run(port=8080)
