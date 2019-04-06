#!/usr/bin/python3
from bluepy import btle

from delegate import SensorDelegate, RingerDelegate
from device import Device

CHARACTERISTIC = 37 #ble module in use characteristic for data

def scan():
    '''Scans for BLE devices and returns information about them
    used essentially for the user to find belonging new 'devices' (sensor|ringer)

    Returns:
        dict: data in json format
    '''

    data = {}

    devices = btle.Scanner().scan(10.0)
    for dev in devices:
        dev_data = {}
        dev_data['addr'] = dev.addr
        dev_data['addrType'] = dev.addrType
        dev_data['rssi'] = dev.rssi
        print ("Device ",dev.addr," (",dev.addrType,"), RSSI=",dev.rssi," dB")

        scan_data = {}
        for (adtype, desc, value) in dev.getScanData():
            scan_data[desc] = value
            print (adtype," | ",desc, " = ", value)
        dev_data['scan_data'] = scan_data

        print ("--------------------------------------------------")
        data[dev.addr] = dev_data

    return data

def receive_sensor_msg(ringer_objs):
    '''Deal with received sensor msg

    Args:
        msg (String): msg from sensor
        ringer_objs (dict): mac:Device
    '''

    def deal_with_sensor_msg(msg):
        print ("PROCESSING SENSOR MSG\n")

        if msg == b"ALARM\n":
            print ("ALARM acknowledged")

            for ringer in ringer_objs.values():
                ringer.send_message("RING\n")

    return deal_with_sensor_msg

def send_command(recipients, command):
    for recipient in recipients.values():
        recipient.send_message(command)

def create_sensor_objects(data, sensors_objs, ringer_objs):
    '''Create sensor objects

    Args:
        data (dict): mac:alias
        sensors_objs (dict): mac:sensor_device
        ringer_objs (dict): mac:ringer_device
    '''

    for mac, alias in data.items():
        print ("Creating sensor with: ", mac, alias)
        try:
            s_delegate = SensorDelegate(alias, receive_sensor_msg(ringer_objs))
            device = Device(alias, CHARACTERISTIC, mac, s_delegate)
            device.withDelegate(s_delegate)
            sensors_objs[mac] = device
        except Exception as e:
            print (str(e))
            return 1    #return error code, so rerun scan
    return 0

def create_ringer_objects(data, ringer_objs):
    '''Create ringer object

    Args:
        data (dict): mac:alias
        ringer_objs (dict): mac:ringer_device
    '''

    for mac, alias in data.items():
        print ("Creating ringer with: ", mac, alias)
        try:
            r_delegate = RingerDelegate(alias) 
            device = Device(alias, CHARACTERISTIC, mac, r_delegate)
            device.withDelegate(r_delegate)
            ringer_objs[mac] = device
        except Exception as e:
            print (str(e))
            return 1    #return error code, so rerun scan
    return 0


