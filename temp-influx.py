#!/usr/bin/env python

import json
from argparse import ArgumentParser
import time
import datetime
import random
from influxdb import InfluxDBClient

parser = ArgumentParser("Read ds18b20 sensor and post to influxDb")
parser.add_argument("--config", required=True)

temp_dir = "/sys/bus/w1/devices/w1_bus_master1/"

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

def get_data_points(sensors):
    iso = time.ctime()
    temp_1 = read_temp(sensors[0]["id"])
    temp_2 = read_temp(sensors[1]["id"])
    json_body = [
            {
                "measurement": "temperature",
                "tags": {"host": "127.0.0.1"},
                "time": datetime.datetime.utcnow(),
                "fields": {
                    "temp_1": temp_1,
                    "temp_2": temp_2,
                    }
                }

            ]

    return json_body

config_file = parser.parse_args().config

with open(config_file) as f:
    config = json.load(f)

if __name__ == "__main__":
    client = InfluxDBClient(
        config["influx_config"]["influx_host"],
        config["influx_config"]["port"],
        config["influx_config"]["user"],
        config["influx_config"]["password"],
        config["influx_config"]["dbname"])

    while True:
        json_body = get_data_points(config["location"][1]["sensors"])
        client.write_points(json_body)
        print (json_body)
        time.sleep(1)

