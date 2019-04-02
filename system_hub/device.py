#!/usr/bin/python3

from bluepy.btle import Peripheral

class Device(Peripheral):

    def __init__(self, name, characteristic, mac):
        super().__init__(mac)

        self.name = name
        self.characteristic = characteristic

    def send_message(self, msg):
        try:
            super().writeCharacteristic(self.characteristic, msg)
        except:
            pass
            #could actually deal with the problem in some way - e.g. reporting it

