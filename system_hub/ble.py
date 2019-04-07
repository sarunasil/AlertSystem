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


def send_command(recipients, command):
    '''send command to all recipients

    Args:
        recipients (set()):
        command (String): command to send
    '''

    for recipient in recipients:
        recipient.send_message(command)

def create_sensor_object(mac, alias, sensors_objs, raise_alarm_func):
    '''Create sensor object

    Args:
        mac (String): device mac address
        alias (String): device alias
        sensors_objs (dict): mac:sensor_device
        raise_alarm_func (func): pass to SensorDelegate
    '''

    print ("Creating sensor with: ", mac, alias)
    try:
        device = Device(alias, CHARACTERISTIC, mac)
        s_delegate = SensorDelegate(device, raise_alarm_func)
        device.withDelegate(s_delegate)

        sensors_objs[mac] = device
    except Exception as e:
        print (str(e))
        return 1    #return error code, so rerun scan
    return 0

def create_ringer_object(mac, alias, ringer_objs):
    '''Create ringer object

    Args:
        mac (String): device mac address
        alias (String): device alias
        ringer_objs (dict): mac:ringer_device
    '''

    print ("Creating ringer with: ", mac, alias)
    try:
        device = Device(alias, CHARACTERISTIC, mac)
        r_delegate = RingerDelegate(device)
        device.withDelegate(r_delegate)

        ringer_objs[mac] = device
    except Exception as e:
        print (str(e))
        return 1    #return error code, so rerun scan
    return 0


