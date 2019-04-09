import threading
import os
import requests

pipe = "/tmp/communication"

# commands to receive:
#   reset (simple reset, or reset and meassure)
#   notify: which updates whole sensors or ringers list

#commands to send:
#   ring (a ringer which is ringing, has ringer alias in it)
#   lost_connection (a device connection has been lost, has device alias in it)
#       Would only be called if connection lost of a long period of time

class Communicator(threading.Thread):

    def __init__(self, reset_func, update_devices_func, scan_func):

        super().__init__()
        self.running = True
        self.pipe = "/tmp/communication"

        self.reset_func = reset_func
        self.update_devices_func = update_devices_func
        self.scan_func = scan_func

    def run(self):

        assert os.path.exists(self.pipe), "Communication pipe has not been created"

        with open(pipe, "r") as pipefile:

            while self.running:

                line = pipefile.readline()

                if line == "RESET\n":#reset ringers and sensors state (stops alarm)
                    self.reset_func()

                elif line == "RESEET_AND_MEASURE\n":#stops alarm and sensors initial value is measured again
                    self.reset_func(measure=True)

                elif line == "SCAN\n": #scan ble devices and post result
                    data = self.scan_func()
                    Communicator.scan_result(data)

                elif line.startswith("NOTIFY"):
                    # msg is in format "NOTIFY:{SENSORS or RINGERS}\n", e.g. "NOTIFY:SENSORS\n" or "NOTIFY:RINGERS\n"
                    msg = line[:-1].split(":")[1]

                    if msg == "SENSORS":
                        print("PULLING LIST OF SENSORS")
                        sensors = self.get_sensors()
                        self.update_devices_func(0, sensors) #0 - sensor; 1 - ringer
                    elif msg == "RINGERS":
                        print("PULLING LIST OF RINGERS")
                        ringers = self.get_ringers()
                        self.update_devices_func(1, ringers) #0 - sensor; 1 - ringer

    @staticmethod
    def get_sensors():
        sensors = requests.get("http://localhost:8080/devices/sensors").json()
        return sensors

    @staticmethod
    def get_ringers():
        ringers = requests.get("http://localhost:8080/devices/ringers").json()
        return ringers

    @staticmethod
    def ring(alias):
        # the assumption is that alias will always be the alias of a sensor
        print("Sending ring")
        # if more data about the alarm needs to be sent to app just include it in the JSON
        requests.post("http://localhost:8080/alarms", json={"alias": alias})

    @staticmethod
    def lost_connection_with_sensor(alias):
        print("Sending lost connection with sensor")
        requests.post("http://localhost:8080/devices/sensors/{0}".format(alias), json={"status": "disconnected"})

    @staticmethod
    def established_connection_with_sensor(alias):
        print("Sending established connection with sensor")
        requests.post("http://localhost:8080/devices/sensors/{0}".format(alias), json={"status": "connected"})

    @staticmethod
    def lost_connection_with_ringer(alias):
        print("Sending lost connection with ringer")
        requests.post("http://localhost:8080/devices/ringers/{0}".format(alias), json={"status": "disconnected"})

    @staticmethod
    def established_connection_with_ringer(alias):
        print("Sending established connection with ringer")
        requests.post("http://localhost:8080/devices/ringers/{0}".format(alias), json={"status": "connected"})

    @staticmethod
    def scan_result(data):
        # ignoring this for now
        print("Sending scan result")
        pass
