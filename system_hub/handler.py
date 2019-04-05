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

                elif line.startswith("NOTIFY"):
                    # msg is in format "NOTIFY:{SENSORS or RINGERS}\n", e.g. "NOTIFY:SENSORS\n" or "NOTIFY:RINGERS\n"
                    msg = line[:-1].split(":")[1]

                    if msg == "SENSORS":
                        print("PULLING LIST OF SENSORS")
                        sensors = requests.get("http://localhost:8080/devices/sensors").json()
                        print(sensors)
                    elif msg == "RINGERS":
                        print("PULLING LIST OF RINGERS")
                        ringers = requests.get("http://localhost:8080/devices/ringers").json()
                        print(ringers)

                    # TODO implementation - do something with the list of sensors and ringers
