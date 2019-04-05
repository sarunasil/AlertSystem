#!/usr/bin/python3

from bluepy.btle import DefaultDelegate

class SensorDelegate(DefaultDelegate):

    def __init__(self, device_name, alarm_func):
        super().__init__()

        self.device_name = device_name
        self.alarm_func = alarm_func

    def handleNotification(self,cHandle,data):

        try:
            print(data)
            self.alarm_func(data)
        except Exception as e:
            print (str(e))

class RingerDelegate(DefaultDelegate):

    def __init__(self, device):
        super().__init__()

        self.device = device

    def handleNotification(self,cHandle,data):

        try:
            print(data)
        except:
            pass
