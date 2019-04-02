#!/usr/bin/python3

from bluepy.btle import DefaultDelegate

class SensorDelegate(DefaultDelegate):

    def __init__(self, device, alarm_func):
        super().__init__()

        self.device = device
        self.alarm_func = alarm_func

    def handleNotification(self,cHandle,data):

        try:
            print(data)
            alarm_func(device.name, data)
        except:
            pass
