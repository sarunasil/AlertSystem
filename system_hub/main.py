
#!/usr/bin/python3
import time
import os

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

def reconnect():
    '''If not all possible devices connected:
        - scan for nearby ble devices
        - create objects if any macs are in sqlite lists
    '''

    global sensors_db, ringers_db
    global sensor_objs, ringer_objs

    if len(sensors_db) == len(sensor_objs) and len(ringers_db) == len(ringer_objs):
        return

    discovered_sensors, discovered_ringers = ble.find_system_devices(sensors_db, ringers_db, sensor_objs, ringer_objs)


    if len(discovered_sensors) + len(sensor_objs) != sensors_db:
        ble.create_sensor_objects(discovered_sensors, sensor_objs, ringer_objs)

    if len(discovered_ringers) + len(ringer_objs) != ringers_db:
        ble.create_ringer_objects(discovered_ringers, ringer_objs)

    print ("Reconnect done.")
    print (str(sensor_objs)+" | "+str(ringer_objs))

def lost_connection(name, mac, type):
    '''Call if lost connection to some device

    Args:
        name (String): device alias
        mac (String): device mac
        type (String): 'sensor' or 'ringer'
    '''

    print ("Lost connection to "+name)

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

def main():
    global sensor_objs, ringer_objs

    while True:
        reconnect()
        ble.check_alive(sensor_objs, ringer_objs, lost_connection)

        time.sleep(5)


if __name__== "__main__":
    setup()
    main()

