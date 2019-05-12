
#!/usr/bin/python3
import time
import os
from queue import Queue
from concurrent.futures import ThreadPoolExecutor

import ble
import communicator
from worker import Worker

#btle Peripherals
sensor_objs = {}    #object list mac:Device
ringer_objs = {}    #object list mac:Device


# seems to indicate that having multiple ble.Peripheral objects
# and trying to connec to them at the same time
# IS thread safe
# https://github.com/IanHarvey/bluepy/issues/126
#jobs like reconnecting or creating new devices
jobs_queue = Queue()
pause_life_check = False

def queue_raise_alarm(alias):
    '''Call to queue an ALARM job to job_queue

    Args:
        alias (String): sensor which raised the alarm alias
    '''
    global jobs_queue
    global pause_life_check

    pause_life_check = True
    jobs_queue.put({'job':'alarm', 'alias':alias})
    print ("QUEUED: alarm")

def queue_connect(jobs_queue, alias, mac, typee):
    '''Call if if want to connect to a device via a new thread

    UPDATE:
    Adds item info into jobs_queue and a worker will
    pick it up whan available - limits the number of threads
    created

    Args:
        alias (String): device alias
        mac (String): device mac
        type (0|1): 0 = 'sensor' or 1 = 'ringer'
    '''

    jobs_queue.put({'job':'connect', 'mac':mac, 'alias':alias, 'typee':typee, 'alarm_func':queue_raise_alarm})
    print ("QUEUED: connect")



def check_alive(jobs_queue, sensor_objs, ringer_objs):
    '''Check if system device is alive - if not or not responding 
    notify that device is lost and remove from connected devices dicts

    Args:
        queue_connect_func (func): func ref to queue new connect request
    '''
    def check(typee, device_objs):
        '''Check one device type
        '''

        for mac, device in list(device_objs.items()):
            try:
                state = device.getState()
                if state != 'conn':
                    raise Exception("state != 'conn'")
            except Exception as e:
                print (str(e))

                if typee == 0:
                    communicator.Communicator.lost_connection_with_sensor(device.alias)
                elif typee == 1:
                    communicator.Communicator.lost_connection_with_ringer(device.alias)


                try:
                    device.disconnect()
                except:
                    pass
                device_objs.pop(mac, None)
                queue_connect(jobs_queue, device.alias, mac, typee) #0 for sensor; 1 for ringer

    check(0, sensor_objs)
    check(1, ringer_objs)



def reset(measure=False):
    '''Enqueue a reset job

    Args:
        measure (Bool): True - reset all devices
                                and make sensors take new measurements
                        False - reset activated devices
    '''

    global jobs_queue

    jobs_queue.put({'job':'reset', 'measure':measure})

def renew_data(typee, devices):
    '''Renew sensors_objs or ringers_objs info depending on typee

    Args:
        typee (0|1): 0 - sensor; 1 - ringer
        ringers (dict): mac:Device
    '''
    global sensor_objs, ringer_objs
    global jobs_queue

    if typee == 0:
        old_devices = sensor_objs
    elif typee == 1:
        old_devices = ringer_objs
    else:
        old_devices = {}

    for mac, device in list(old_devices.items()):
        try:
            device.disconnect()
        except:
            pass
        old_devices.pop(mac, None)

    print ("Renew data received: ", devices)
    for device_data in devices:
        print (device_data)
        #typee: 0 for sensor, 1 for ringer
        queue_connect(jobs_queue, device_data['alias'], device_data['mac'], typee)

    return len(devices)

def setup():
    global  sensor_objs, ringer_objs
    global jobs_queue

    communicator.Communicator(reset, renew_data, ble.scan).start()

    time.sleep(5)

    #call these to get
    sensors_len = renew_data(0, communicator.Communicator.get_sensors())
    ringers_len = renew_data(1, communicator.Communicator.get_ringers())


    #create workers to deal with devices loosing connection and reconnecting
    number_of_threads = min(3, sensor_len + ringer_len + 1) #make sure there are enough threads
    thread_executor =  ThreadPoolExecutor(number_of_threads)
    for i in range(0, number_of_threads):
        thread_executor.submit(Worker, i, jobs_queue, sensor_objs, ringer_objs)
    print ('\nSetup DONE\n')

def main():
    global sensor_objs, ringer_objs
    global jobs_queue

    counter = 1
    while True:
        #go through all sensors
        #ringers don't send data, so don't bother
        for sensor in list(sensor_objs.values()):
            try:
                if sensor.waitForNotifications(1.0):
                    continue
            except Exception as e:
                # Allow check_alive to deal with connections
                # this code is only concerned with notifications
                print (str(e))

        check_alive(jobs_queue, sensor_objs, ringer_objs)
        print (counter, end='\r')
        counter+=1
        time.sleep(3)

if __name__== "__main__":
    setup()
    main()

