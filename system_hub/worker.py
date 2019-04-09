
#!/usr/bin/python3
import time
import os
from queue import Queue


import ble
import communicator


class Worker:
    def __init__(self, iden, jobs_queue, sensor_objs, ringer_objs):
        '''function executed as a thread that tries
        to continuously reconnect to lost device
        or newly added devices.
        Tbf, to whatever it finds in the jobs_queue

        Args:
            iden (int): for debug threat identifier
            jobs_queue (dict): json like dict object with mac and alias of the device
            sensor_objs (dict): ref to global sensor_objs
            ringer_objs (dict): ref to global ringer_objs
        '''
        self.iden = iden
        self.sensor_objs = sensor_objs
        self.ringer_objs = ringer_objs

        #work until killed
        while True:
            job = jobs_queue.get() #blocks if no work available
            print (iden, "got job", job['job'])

            if job['job'] == 'connect':
                self.__connect(job)
            elif job['job'] == 'alarm':
                self.__raise_alarm(job['alias'])
            elif job['job'] == 'reset':
                if job['measure']:
                    self.__reset_and_measure()
                else:
                    self.__reset()
            else:
                pass
            jobs_queue.task_done()

    def __connect(self, job):
        retry_period = 3 #seconds
        #repeat until connected
        while True:
            if job['typee'] == 0:
                error = ble.create_sensor_object(job['mac'], job['alias'], self.sensor_objs, job['alarm_func'])
                if error == 0:
                    communicator.Communicator.established_connection_with_sensor(job['alias'])
                    break
            elif job['typee'] == 1:
                error = ble.create_ringer_object(job['mac'], job['alias'], self.ringer_objs)
                if error == 0:
                    communicator.Communicator.established_connection_with_ringer(job['alias'])
                    break
            else:
                break

            time.sleep(retry_period)

        #send notification that device X is reconnected
        print (self.iden, "Connected to ", job['alias'])

    def __raise_alarm(self, raiser):
        '''Alarm was sounded by sensor with alias 'raiser'
        Notify all ringers

        Args:
            raiser (String): sensor alias
        '''


        resend_period = 5#seconds

        communicator.Communicator.ring(raiser)

        while True:
            #resend msg to all not ack ringers (ringer.dev_status!=1)
            #untill all ringers are ringing (ringer.dev_status==1)
            resend = False
            for ringer in self.ringer_objs.values():
                if ringer.dev_status != 1: #if not ack ringing
                    resend = True
            if not resend: #stop sending
                break

            #resend
            for ringer in list(self.ringer_objs.values()):
                if ringer.dev_status != 1:
                    ringer.send_message("RING\n")

            time.sleep(resend_period)
            print ("SENDING LOOP END")
        print ("OUT OF SENDING LOOP")

    def __reset(self):
        '''Reset only sensors and ringers that were activated
        by an alarm
        '''

        resend_period = 2#seconds
        #repeat until all devices have ack their reset
        while True:
            activated_devices = []
            for device in list({**self.sensor_objs, **self.ringer_objs}.values()):
                if device.dev_status == 1:
                    activated_devices.append(device)

            if not activated_devices:
                break

            ble.send_command(activated_devices, "RESET\n")
            time.sleep(resend_period)

    def __reset_and_measure(self):
        '''Reset all devices and take new measurements

        IMPORTANT:
        Does not wait for confirmation - one time execution.
        '''

        resend_period = 2#seconds
        ble.send_command(self.sensor_objs.values(), "RESET_AND_MEASURE\n")
        ble.send_command(self.ringer_objs.values(), "RESET\n")
        time.sleep(resend_period)

