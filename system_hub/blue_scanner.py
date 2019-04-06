from bluepy.btle import Scanner

def scan():
    '''Scans for BLE devices and returns information about them
    used essentially for the user to find belonging new 'devices' (sensor|ringer)

    Returns:
        dict: data in json format
    '''

    data = {}

    devices = Scanner().scan(10.0)
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

if __name__ == '__main__':
    print (scan())