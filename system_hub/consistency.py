#!/usr/bin/python3
import os
import time
import sqlite3
import threading


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
DATABASE_FILE = os.path.join(CURRENT_DIR, "database/db.sqlite")

def get_sensors(path):
    '''Return sensors data from sqlite

    Args:
        path (String): to sqlite db
    '''
    try:
        data = {}
        db = sqlite3.connect(path)
        # return {'00:15:83:30:d4:22': "KIRK_SENSOR_1"}

        # Get a cursor object
        cursor = db.cursor()
        cursor.execute('''SELECT mac, name FROM device where type = 0''')
        for row in cursor:
            data[row[0]] = row[1]
        return data
    except:
        return None

def get_ringers(path):
    '''Return ringers data from sqlite

    Args:
        path (String): to sqlite db
    '''
    try:
        data = {}
        db = sqlite3.connect(path)
        # return {'00:15:83:30:d4:22': "KIRK_SENSOR_1"}

        # Get a cursor object
        cursor = db.cursor()
        cursor.execute('''SELECT mac, name FROM device where type = 1''')
        for row in cursor:
            data[row[0]] = row[1]
        return data
    except:
        return None


class Manager (threading.Thread):
    manager_run_period = 60 #seconds

    def __init__(self, path, action):
        '''Init

        Args:
            path (String): path to database file
            action (func): action to execute
        '''

        threading.Thread.__init__(self)
        self.path = path
        self.action = action
        self.work = True #run while True

    def run(self):
        while self.run:
            sensors_data = get_sensors(self.path)
            ringers_data = get_ringers(self.path)

            if sensors_data is not None and ringers_data is not None:
                self.action(sensors_data, ringers_data)
            time.sleep(Manager.manager_run_period)

def setup_defaults(path):
    '''Create sqlite default database if not present

    Args:
        path (String): path to location
    '''

    try:
        db = sqlite3.connect(path)

        # Get a cursor object
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS device(id INTEGER PRIMARY KEY, mac TEXT UNIQUE, name TEXT UNIQUE, type INTEGER)''')

        # insert_sql = ''' INSERT INTO device(mac, name, type)
        #       VALUES(?,?,?) '''
        # cursor.execute(insert_sql, ('00:15:83:30:d4:22', 'KIRK_SENSOR_1', 0))
        # cursor.execute(insert_sql, ('00:15:83:40:7c:3d', 'KIRK_RINGER_1', 1))

        db.commit()
    except sqlite3.Error as e:
        print(e)
    finally:
        db.close()

def setup_consistency(manager_func, path=DATABASE_FILE):
    '''Setups database manager/checker thread

    Args:
        manager_func (func): to be called by manager after refreshing data
        path (String, optional): Defaults to DATABASE_FILE.

    Returns:
        Manager: sqlite manager
    '''


    setup_defaults(path)

    manager = Manager(path, manager_func)
    manager.start()

    return manager

