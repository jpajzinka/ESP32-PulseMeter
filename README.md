# ESP32-PulseMeter
This repository contains quick and dirty Micropython ESP32 Pulse Sensor implementation which can be used to colect you water and gas meter pulses and calulate 15 minutes consumption.

The code, client() method is prepared for integration with ThingsBoard (https://thingsboard.io/)

To succesfully integrate then solution with ThingsBoard server you need to configure reed_setting.py file, especially all following fields

device_id = "thingsboard device acces token"
LPlen = 15 #telemetry frequency in minutes
channel = "LP15" # telemetry name
temp_sensor = "None" #type of temp sensor if attached to esp32
#temp_sensor = "DHT22"
#temp_sensor = "DS18X20"
#temp_sensor = "dummy"
threshold = 50 #temp sensor threshold - higher value ignored
tempPin = 12 #temp sensor pin
wifiSSID = "your wifi name"
wifiPWD = "wifi password"
server="your thingsboard server IP"
port="your thingsboad server port"

