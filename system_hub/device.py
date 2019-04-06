#!/usr/bin/python3

from bluepy.btle import Peripheral

class Device(Peripheral):

    def __init__(self, alias, characteristic, mac, handler):
        super().__init__(mac)

        self.alias = alias
        self.characteristic = characteristic
        self.handler = handler #maybe save it here if it's getting removed

    def send_message(self, msg):
        try:
            print("Sending message: "+msg)
            super().writeCharacteristic(self.characteristic, msg.encode('utf-8'))
        except Exception as e:
            print (str(e))
            #could actually deal with the problem in some way - e.g. reporting it

