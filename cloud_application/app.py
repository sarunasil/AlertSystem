from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
import smtplib
import getpass
import datetime
import logging
import os
from pathlib import Path
from model import get_receivers_emails, get_receivers, get_receiver, delete_receivers, delete_receiver, receiver_email_exists, create_receiver, is_valid_user, \
    register_user, change_user_password, get_user_visualisation_key

# logging configuration
LOG_FILE = "/var/log/alarms.log"
Path(LOG_FILE).touch()  # make sure log file is created

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
filehandler = logging.FileHandler(LOG_FILE)
filehandler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
filehandler.setFormatter(formatter)
logger.addHandler(filehandler)

# app config. and init.
app = Flask(__name__)
CORS(app)
@app.errorhandler(Exception)
def handler(e):
    if getattr(e, "code", None) is not None:
        return jsonify({"msg": str(e)}), e.code


app.config['JWT_SECRET_KEY'] = os.environ["JWT_SECRET_KEY"]
jwt = JWTManager(app)

smtp_port = 465
smtp_server = "smtp.gmail.com"
email = input("Email:")
password = getpass.getpass("Password:")

message = """
Received an alarm on {0} UTC
\n
{1}"""


@app.route('/register', methods=['POST'])
@jwt_required
def register():

    if request.json is None:
        abort(400, "Expecting JSON body.")

    if request.json.keys() != {"username", "password"}:
        abort(400, "Expecting JSON body with username and password.")

    user = get_jwt_identity()
    if user != "admin":
        abort(403, "Only the root user can register new accounts.")

    username = request.json.get('username', None)
    user_password = request.json.get('password', None)

    if username == "" or user_password == "":
        abort(400, "Username and password cannot be empty.")

    if not register_user(username, user_password):
        abort(409, "Username is already registered")

    return jsonify({"msg": "Account successfully created."})


@app.route('/login', methods=['POST'])
def login():

    if request.json is None:
        abort(400, "Expecting JSON body.")

    if request.json.keys() != {"username", "password"}:
        abort(400, "Expecting JSON body with username and password.")

    username = request.json.get('username', None)
    user_password = request.json.get('password', None)

    if username is None or user_password is None or not is_valid_user(username, user_password):
        abort(401, "Authentication failure.")

    access_token = create_access_token(identity=username)
    return jsonify({"token": access_token}), 200


@app.route('/account', methods=['PUT'])
@jwt_required
def change_password():

    if request.json is None:
        abort(400, "Expecting JSON body.")

    if request.json.keys() != {"old_password", "new_password"}:
        abort(400, "Expecting JSON body with passwords.")

    user = get_jwt_identity()
    old_password = request.json["old_password"]
    new_password = request.json["new_password"]

    if change_user_password(user, old_password, new_password):
        return jsonify({"msg": "Password has been updated"})
    else:
        abort(401, "Authentication failure.")


@app.route('/visualisation', methods=['GET'])
@jwt_required
def visualisation_key():

    user = get_jwt_identity()

    return jsonify({"key": get_user_visualisation_key(user)})


@app.route('/receivers', methods=['POST', 'GET', 'DELETE'])
@jwt_required
def api_receivers():

    if request.method == 'GET':
        return jsonify(get_receivers())

    elif request.method == 'DELETE':
        return jsonify(delete_receivers())

    elif request.method == 'POST':
        body = request.json

        if body is None:
            abort(400, "Expecting JSON body.")

        if body.keys() != {"email"}:
            abort(400, "Invalid JSON content.")

        if body["email"] == "":
            abort(400, "Cannot register empty email address.")

        if receiver_email_exists(body["email"]):
            abort(409, "Email receiver already exists.")

        return jsonify(create_receiver(body["email"]))


@app.route('/receivers/<uuid:index>', methods=['GET', 'DELETE'])
@jwt_required
def api_receivers_instance(index):

    email_object = get_receiver(index)

    if email_object is None:
        abort(404, "Email receiver with the given ID doesn't exist.")

    if request.method == 'GET':

        return jsonify(email_object)

    elif request.method == 'DELETE':

        delete_receiver(email_object)

        return jsonify(email_object)


@app.route('/alarms', methods=['POST', 'GET'])
@jwt_required
def api_alert():

    user = get_jwt_identity()

    email_addresses = get_receivers_emails()

    if request.method == 'POST':
        body = request.json

        if body is None:
            abort(400, "Expecting JSON body.")

        if body.keys() != {"msg"}:
            abort(400, "Invalid JSON content.")

        msg = body['msg']

        logger.info("Received alarm from {0} with message - {1}, potential receivers - {2}".format(user, msg, email_addresses))

        logger.warning(user)

        if len(email_addresses) > 0 and request.args.get("with_email", "true") == "true":
            logger.info("Sending alarm to receivers - {0}".format(email_addresses))
            # send the email acknowledging an alarm
            email_msg = message.format(datetime.datetime.now(), msg)
            server_ssl = smtplib.SMTP_SSL(smtp_server, smtp_port)
            server_ssl.login(email, password)
            server_ssl.sendmail(email, email_addresses, email_msg)
            server_ssl.quit()

        logger.info("----------------------------------------------------------------------------")

        return jsonify({"msg": "Alarm acknowledged."})

    elif request.method == 'GET':

        with open(LOG_FILE) as fh:
            content = fh.read()

        return '\n'.join(reversed(content.split("\n")))


app.run(host='0.0.0.0', port=8080)
