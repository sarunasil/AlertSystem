#!/usr/bin/python3

from bluepy.btle import Peripheral

class Device(Peripheral):

    def __init__(self, alias, characteristic, mac):
        super().__init__(mac)

        self.alias = alias
        self.characteristic = characteristic
        self.dev_status = 0 # 0 - no alarm, 1 - alarm


    def send_message(self, msg):
        try:
            print("Sending message: "+msg)
            super().writeCharacteristic(self.characteristic, msg.encode('utf-8'))
        except Exception as e:
            print (str(e))
            #could actually deal with the problem in some way - e.g. reporting it

