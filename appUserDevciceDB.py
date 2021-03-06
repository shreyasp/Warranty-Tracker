#!/usr/local/bin/python3


# Copyright (c) 2015 Shreyas Patil
# The MIT License (MIT). Please refer to License.md


__author__ = 'shreyas'


from pymongo import errors
from datetime import datetime, timedelta
from tablesUtil import *

from dateutil.relativedelta import *


class AppUserDeviceDB():

    def __init__(self, userid, deviceName, deviceType, devicePurchaseDate, warrantyPeriod):
        self.userid = userid
        self.deviceName = deviceName
        self.deviceType = deviceType
        self.devicePurchaseDate = devicePurchaseDate
        self.warrantyPeriod = warrantyPeriod


    # Method to add new device to db
    def addNewUserDevice(self, db):

        deviceCollection = db.deviceCollection

        warrantyDate = calculate_warranty_date(self.devicePurchaseDate, self.warrantyPeriod)

        device = { 'device_name'    : self.deviceName,\
                   'device_type'    : self.deviceType,\
                   'purchase_date'  : self.devicePurchaseDate,\
                   'warranty_date'  : warrantyDate }

        find_query   = {'_id': self.userid}
        update_query = {'$addToSet' : {'devices': device}}

        try:
            userDevices = deviceCollection.find_one(find_query)
        except errors.PyMongoError as deviceNameError:
            print('No such collection exists or database connection issue', deviceNameError)

        if userDevices is None:
            upsert = True
        else:
            upsert = False

        try:
            name = deviceCollection.update_one(find_query, update_query, upsert=upsert)
        except errors.PyMongoError as err:
            print('Device was not inserted', err)



def calculate_warranty_date(purchaseDate, warrantyPeriod):
    # Convert the warranty period from months to weeks
    convertedWeeks = (int(warrantyPeriod)/12) * 52
    warrantyDate = purchaseDate + timedelta(weeks=convertedWeeks)

    return(warrantyDate)


def populate_user_device_table(userid, db):
    deviceCollection = db.deviceCollection

    print(userid)
    try:
        user = deviceCollection.find_one({'_id': userid})
    except errors.PyMongoError as err:
        print('No such or collection exists in the DB', err)

    # Check whether user has added any devices to his profile, else just return back None
    if user is not None:
        devices = user['devices']
    else:
        print('None returned')
        return(None)

    # Once we have the devices that user has we will create the code make a table object out of it
    # Before creating a table we have to format data into appropriate format
    formatted_device_data = parse_and_format_user_devices_data(devices)

    table = []

    table.append(create_user_device_objects(formatted_device_data[0]))
    table.append(create_user_device_objects(formatted_device_data[1]))

    return(table)


def parse_and_format_user_devices_data(devices):
    # Here devices is list of dictionaries
    formatted_data = []
    in_warr_device = []
    out_warr_device = []

    today = datetime.today()

    for device in devices:
        warranty_date = device['warranty_date']

        device['purchase_date']= device['purchase_date'].strftime('%d-%m-%Y')
        device['warranty_date']= device['warranty_date'].strftime('%d-%m-%Y')

        if(warranty_date > today):
            in_warr_device.append(device)
        else:
            out_warr_device.append(device)

    formatted_data.append(in_warr_device)
    formatted_data.append(out_warr_device)

    # Now we need to create two parts for in warranty and out of warranty devices
    return(formatted_data)
