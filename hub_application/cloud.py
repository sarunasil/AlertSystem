from flask import Flask, request, jsonify, abort
import smtplib
import getpass
import datetime
import logging
from pathlib import Path


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


receivers = []  # a list of the receivers' email addresses, TODO this must be hardcoded before starting the application

smtp_port = 465
smtp_server = "smtp.gmail.com"
email = input("Email:")
password = getpass.getpass("Password:")

message = """
Received an alarm on {0} UTC
\n
{1}"""


@app.route('/alarms', methods=['POST', 'GET'])
def alert():

    if request.method == 'POST':
        body = request.json

        if body is None:
            abort(400, "Expecting JSON body.")

        if body.keys() != {"msg"}:
            abort(400, "Invalid JSON content.")

        msg = body['msg']

        logger.warning("Received alarm with message - {0}".format(msg))

        if request.args.get("with_email", "true") == "true":
            logger.info("Sending alarm to receivers - {0}".format(receivers))
            # send the email acknowledging an alarm
            email_msg = message.format(datetime.datetime.now(), msg)
            server_ssl = smtplib.SMTP_SSL(smtp_server, smtp_port)
            server_ssl.login(email, password)
            server_ssl.sendmail(email, receivers, email_msg)
            server_ssl.quit()
        logger.info("----------------------------------------------------------------------------")

        return jsonify({"msg": "Alarm acknowledged."})

    elif request.method == 'GET':

        with open(LOG_FILE) as fh:
            content = fh.read()

        return content


app.run(host='0.0.0.0', port=8080)
