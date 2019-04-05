
#!/usr/bin/python3
import time
import os
import threading


import cloud
import ble
import consistency

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
DATABASE_PATH = os.path.join(CURRENT_DIR, "database/db.sqlite")  #path to local database

#from database
sensors_db = {}     #sqlite sensor list mac:name
ringers_db = {}     #sqlite ringer list mac:name

#btle Peripherals
sensor_objs = {}    #object list mac:Device
ringer_objs = {}    #object list mac:Device

db_manager = None

def connect():
    '''
        - scan for nearby ble devices
        - create objects if any macs are in sqlite lists
    '''

    global sensors_db, ringers_db
    global sensor_objs, ringer_objs

    if len(sensors_db) == len(sensor_objs) and len(ringers_db) == len(ringer_objs):
        return 0

    discovered_sensors, discovered_ringers = ble.find_system_devices(sensors_db, ringers_db, sensor_objs, ringer_objs)


    if len(discovered_sensors) + len(sensor_objs) != sensors_db:
        ble.create_sensor_objects(discovered_sensors, sensor_objs, ringer_objs)

    if len(discovered_ringers) + len(ringer_objs) != ringers_db:
        ble.create_ringer_objects(discovered_ringers, ringer_objs)

    print (str(sensor_objs)+" | "+str(ringer_objs))
    return 1



class Reconnecter(threading.Thread):
    '''Threat that tries to continuously reconnect to lost device
    '''

    reconnect_period = 3 #seconds

    def __init__(self, data, typee):
        '''Init

        Args:
            data ({mac:name}): data of device
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

        cloud.reconnected_device(list(self.data.keys())[0])

def lost_connection(name, mac, typee):
    '''Call if lost connection to some device

    Args:
        name (String): device alias
        mac (String): device mac
        type (0|1): 0 = 'sensor' or 1 = 'ringer'
    '''

    input("Lost connection to: "+name+ " " + mac )
    #start threat to try reconnecting
    reconnecter = Reconnecter({mac : name}, typee)
    reconnecter.start()

def reset_all():
    global sensor_objs, ringer_objs

    ble.send_command({**sensors_db, **ringer_objs}, "RESET\n")

def take_new_measurement():
    global sensor_objs

    ble.send_command(sensor_objs, "RESET_AND_MEASURE\n")

def renew_data(sensors, ringers):
    '''Renew sensors_db and ringers_db info

    Args:
        sensors (dict): mac:Device
        ringers (dict): mac:Device
    '''
    global sensors_db, ringers_db

    sensors_db = sensors
    ringers_db = ringers


def setup():
    global sensors_db, ringers_db, db_manager

    db_manager = consistency.setup_consistency(renew_data, DATABASE_PATH)

    time.sleep(2)
    while connect() == 1:
        continue

def main():
    global sensor_objs, ringer_objs


    while True:
        #go through all sensors
        #ringers don't send data, so don't bother
        for _, sensor in sensor_objs.items():
            try:
                print ("notif from: ",sensor.name)
                if sensor.waitForNotifications(1.0):
                    continue
            except Exception as e:
                # Allow ble.check_alive to deal with connections
                # this code is only concerned by notifications
                print (str(e))

        ble.check_alive(sensor_objs, ringer_objs, lost_connection)
        time.sleep(1)

if __name__== "__main__":
    setup()
    main()

