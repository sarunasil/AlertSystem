
#!/usr/bin/python3
import time
import os
import threading


import ble
import communicator
import requests

#btle Peripherals
sensor_objs = {}    #object list mac:Device
ringer_objs = {}    #object list mac:Device


class Reconnecter(threading.Thread):
    '''Threat that tries to continuously reconnect to lost device
    '''

    reconnect_period = 3 #seconds

    def __init__(self, data, typee):
        '''Init

        Args:
            data ({mac:alias}): data of device
            typee (0|1): 0 - sensor; 1 - ringer
        '''
        super().__init__()

        self.data = data
        self.typee = typee
        self.work = True #run while True

    def run(self):
        global sensor_objs, ringer_objs
        while self.work:
            if self.typee == 0:
                error = ble.create_sensor_objects(self.data, sensor_objs, ringer_objs)
                if error == 0:
                    break
            elif self.typee == 1:
                error = ble.create_ringer_objects(self.data, ringer_objs)
                if error == 0:
                    break
            else:
                break
            time.sleep(Reconnecter.reconnect_period)

        #send notification that device X is reconnected
        print ("Connected: ", self.data)

def connect(alias, mac, typee):
    '''Call if if want to connect to a device via a new threat

    Args:
        alias (String): device alias
        mac (String): device mac
        type (0|1): 0 = 'sensor' or 1 = 'ringer'
    '''

    #start threat to try reconnecting
    reconnecter = Reconnecter({mac : alias}, typee)
    reconnecter.start()


def check_alive(sensor_objs, ringer_objs):
    '''Check if system device is alive - if not or not responding 
    notify that device is lost and remove from connected devices dicts

    Args:
        sensor_objs (dict): mac:sensor_alias
        ringer_objs (dict): mac:ringer_alias
    '''
    def check(typee, device_objs):
        '''Check one device type
        '''

        for mac, device in list(device_objs.items()):
            try:
                state = device.getState()
                if state != 'conn':
                    raise Exception("state != 'conn'")
            except Exception as e:
                print (str(e))

                try:
                    device.disconnect()
                except:
                    pass
                device_objs.pop(mac, None)
                connect(device.alias, mac, typee) #0 for sensor; 1 for ringer

    check(0, sensor_objs)
    check(1, ringer_objs)

def reset(measure=False):
    global sensor_objs, ringer_objs

    if measure:
        ble.send_command(sensor_objs, "RESET_AND_MEASURE\n")
        ble.send_command(ringer_objs, "RESET\n")
    else:
        ble.send_command({**sensor_objs, **ringer_objs}, "RESET\n")

def renew_data(typee, devices):
    '''Renew sensors_objs or ringers_objs info depending on typee

    Args:
        typee (0|1): 0 - sensor; 1 - ringer
        ringers (dict): mac:Device
    '''
    global sensor_objs, ringer_objs

    if typee == 0:
        old_devices = sensor_objs
    elif typee == 1:
        old_devices = ringer_objs
    else:
        old_devices = {}

    for mac, device in list(old_devices.items()):
        try:
            device.disconnect()
        except:
            pass
        old_devices.pop(mac, None)

    print (devices)
    for device_data in devices.values():
        print (device_data)
        #typee: 0 for sensor, 1 for ringer
        connect(device_data['alias'], device_data['mac'], typee)


def setup():
    communicator.Communicator(reset, renew_data, ble.scan).start()

    time.sleep(5)

    #call these to initiate NOTIFY PIPE MSG
    renew_data(0, requests.get("http://localhost:8080/devices/sensors").json())
    renew_data(1, requests.get("http://localhost:8080/devices/ringers").json())


def main():
    global sensor_objs, ringer_objs

    #TODO IMPLEMENT A THREAT POOL and task queue
    #unmonitored spawning of threats is bound to create problems
    #https://stackoverflow.com/questions/19369724/the-right-way-to-limit-maximum-number-of-threads-running-at-once
    counter = 1
    while True:
        #go through all sensors
        #ringers don't send data, so don't bother
        for _, sensor in sensor_objs.items():
            try:
                if sensor.waitForNotifications(1.0):
                    continue
            except Exception as e:
                # Allow ble.check_alive to deal with connections
                # this code is only concerned by notifications
                print (str(e))

        check_alive(sensor_objs, ringer_objs)
        time.sleep(1)
        print (counter, end='\r')
        counter+=1

if __name__== "__main__":
    setup()
    main()

