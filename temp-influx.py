#!/usr/bin/env python

import time
import datetime
import random
from influxdb import InfluxDBClient

influx_host = 'raspberrypi-unifi.local'
host = '127.0.0.1'
port = 8086
dbname = 'home'
user = 'grafana'
password = 'hidden'

temp_dir = "/sys/bus/w1/devices/w1_bus_master1/"
temp_1_name = "28-00000bc1308b"
temp_2_name = "28-00000bc92225"

client = InfluxDBClient(influx_host, port, user, password, dbname)

def temp_raw(name):
    f = open(temp_dir + name + "/w1_slave", 'r')
    lines = f.readlines()
    f.close
    return lines

def read_temp(name):
    lines = temp_raw(name)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = temp_raw()
    temp_output = lines[1].find('t=')
    if temp_output != -1:
        temp_string = lines[1].strip()[temp_output+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

def get_data_points():
    iso = time.ctime()
    temp_1 = read_temp(temp_1_name)
    temp_2 = read_temp(temp_2_name)
    json_body = [
            {
                "measurement": "temperature",
                "tags": {"host": host},
                "time": datetime.datetime.utcnow(),
                "fields": {
                    "temp_1": temp_1,
                    "temp_2": temp_2,
                    }
                }

            ]

    return json_body


while True:
    json_body = get_data_points()
    client.write_points(json_body)
    print (json_body)
    time.sleep(1)
