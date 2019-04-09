#!/usr/bin/python3

from bluepy.btle import DefaultDelegate

class SensorDelegate(DefaultDelegate):

    def __init__(self, device, raise_alarm_func):
        '''Deals with incoming messages

        Args:
            device (Device): device this is attached to
            raise_alarm_func (func): func to be called 
            to queue an alarm job
        '''
        super().__init__()

        self.device = device
        self.raise_alarm_func = raise_alarm_func

    def handleNotification(self,cHandle,data):

        print(data)
        if data == b"ALARM\n":
            print ("ALARM acknowledged")

            if self.device.dev_status == 0:
                self.raise_alarm_func(self.device.alias)
            self.device.dev_status = 1
            self.device.send_message("ACK\n")
        elif data == b'RESET_ACK\n':
            print ("SENSOR ACK RESET")

            self.device.dev_status = 0



class RingerDelegate(DefaultDelegate):

    def __init__(self, device):
        super().__init__()

        self.device = device

    def handleNotification(self,cHandle,data):

        print(data)
        if data == b"ACK\n":
            print ("RINGER ACK ALARM")

            self.device.dev_status = 1
        elif data == b'RESET_ACK\n':
            print ("RINGER ACK RESET")

            self.device.dev_status = 0
