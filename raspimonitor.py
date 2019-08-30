#!/usr/bin/env python3

##
## Used these repositories for inspiration : 
## - https://github.com/Sennevds/system_sensors
## - https://github.com/LarsBergqvist/RPiClient_MQTT

import paho.mqtt.publish as publish
from gpiozero import CPUTemperature
from re import findall
import time
import psutil
import sys
import yaml
import socket
import os
import threading, time, signal
from datetime import timedelta
import datetime as dt
import pytz
from pytz import timezone

# Variables
UTC = pytz.utc
DEFAULT_TIME_ZONE = timezone('Europe/Amsterdam')#Local Time zone
SYSFILE = '/sys/devices/platform/soc/soc:firmware/get_throttled'
CONFIGFILE = 'configuration.yaml'

def utc_from_timestamp(timestamp: float) -> dt.datetime:
    """Return a UTC time from a timestamp."""
    return UTC.localize(dt.datetime.utcfromtimestamp(timestamp))

def as_local(dattim: dt.datetime) -> dt.datetime:
    """Convert a UTC datetime object to local time zone."""
    if dattim.tzinfo == DEFAULT_TIME_ZONE:
        return dattim
    if dattim.tzinfo is None:
        dattim = UTC.localize(dattim)

    return dattim.astimezone(DEFAULT_TIME_ZONE)

def get_last_boot():
    return str(as_local(utc_from_timestamp(psutil.boot_time())).isoformat())

def get_temp():
    cpu = CPUTemperature()
    return str(cpu.temperature)

def get_disk_usage():
    return str(psutil.disk_usage('/').percent)

def get_memory_usage():
    return str(psutil.virtual_memory().percent)

def get_cpu_usage():
    return str(psutil.cpu_percent(interval=None))

def get_rpi_power_status():
    _throttled = open(SYSFILE, 'r').read()[:-1]
    _throttled = _throttled[:4]
    if _throttled == '0':
        return 'Everything is working as intended'
    elif _throttled == '1000':
        return 'Under-voltage was detected, consider getting a uninterruptible power supply for your Raspberry Pi.'
    elif _throttled == '2000':
        return 'Your Raspberry Pi is limited due to a bad powersupply, replace the power supply cable or power supply itself.'
    elif _throttled == '3000':
        return 'Your Raspberry Pi is limited due to a bad powersupply, replace the power supply cable or power supply itself.'
    elif _throttled == '4000':
        return 'The Raspberry Pi is throttled due to a bad power supply this can lead to corruption and instability, please replace your changer and cables.'
    elif _throttled == '5000':
        return 'The Raspberry Pi is throttled due to a bad power supply this can lead to corruption and instability, please replace your changer and cables.'
    elif _throttled == '8000':
        return 'Your Raspberry Pi is overheating, consider getting a fan or heat sinks.'
    else:
        return 'There is a problem with your power supply or system.'

def publish_message(config, mqttclient, topic, message):
    
    mqtt_broker = config['server']
    mqtt_port = config['port']
    mqtt_username = config['username']
    mqtt_password = config['password']
    
    print("Publishing to MQTT topic: " + topic)
    print("Message: " + message)

    publish.single(topic, message, retain=True, hostname=mqtt_broker, 
                    port=mqtt_port, client_id=mqttclient, auth={'username':mqtt_username, 'password':mqtt_password})

if __name__ == '__main__':
    
    scriptdir = os.path.dirname(__file__)
    CONFIGPATH = os.path.join(scriptdir, CONFIGFILE)
    print(CONFIGPATH)
    config = yaml.safe_load(open(CONFIGPATH, 'r'))['mqtt']
    
    time.sleep(5)
    cu = get_cpu_usage()
    
    computer_name = socket.gethostname()
    print("Doing measurements for: " + computer_name)

    publish_message(config, computer_name, "Home/" + computer_name + "/Temp", get_temp())
    publish_message(config, computer_name, "Home/" + computer_name + "/DiskUsagePercent", get_disk_usage())
    publish_message(config, computer_name, "Home/" + computer_name + "/MemoryUsagePercent", get_memory_usage())
    publish_message(config, computer_name, "Home/" + computer_name + "/CpuUsagePercent", cu)
    publish_message(config, computer_name, "Home/" + computer_name + "/LastBoot", get_last_boot())
    publish_message(config, computer_name, "Home/" + computer_name + "/PowerStatus", get_rpi_power_status())
    