import threading
import os
import requests

pipe = "/tmp/communication"


class Communicator(threading.Thread):

    def __init__(self):

        super().__init__()
        self.running = True
        self.pipe = "/tmp/communication"

    def run(self):

        assert os.path.exists(self.pipe), "Communication pipe has not been created"

        with open(pipe, "r") as pipefile:

            while self.running:

                line = pipefile.readline()

                if line == "STOP\n":

                    print("STOPPING RINGERS")  # TODO implementation for stopping ringers

                elif line == "NOTIFY\n":
                    print("PULLING LIST OF SENSORS AND RINGERS AND UPDATING CONNECTIONS")
                    # TODO implementation - do something with the list of sensors and ringers
                    sensors = requests.get("http://localhost:8080/devices/sensors").json()
                    ringers = requests.get("http://localhost:8080/devices/ringers").json()
                    print(sensors, ringers)
