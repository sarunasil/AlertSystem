from flask import Flask, request, jsonify, abort
import smtplib
import getpass
import datetime

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


@app.route('/alarms', methods=['POST'])
def alert():

    body = request.json

    if body is None:
        abort(400, "Expecting JSON body.")

    if body.keys() != {"msg"}:
        abort(400, "Invalid JSON content.")

    msg = body['msg']
    email_msg = message.format(datetime.datetime.now(), msg)

    # send the email
    server_ssl = smtplib.SMTP_SSL(smtp_server, smtp_port)
    server_ssl.login(email, password)
    server_ssl.sendmail(email, receivers, email_msg)
    server_ssl.quit()

    return jsonify({"msg": "Alarm acknowledged."})


app.run(host='0.0.0.0', port=8080)
