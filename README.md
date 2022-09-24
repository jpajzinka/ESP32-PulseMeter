# ESP32-PulseMeter
This repository contains quick and dirty Micropython ESP32 Pulse Sensor implementation which can be used to colect you water and gas meter pulses and calulate 15 minutes consumption. The usage of ULP makes this code usable for battery only solutions.

<b>ULP ussage</b>
To implement a pulse sensor in micropython is fairly simple - however the trick is to make a batery effective solution, where in my case the ULP code is the key. The ULP code as such is inspired by code found on this forum https://esp32.com/viewtopic.php?t=13638 with following tweaks

<code>
  #1.
  # connect GPIO to the RTC subsystem so the ULP can read it
  WRITE_RTC_REG(RTC_IO_TOUCH_PAD0_REG, RTC_IO_TOUCH_PAD0_MUX_SEL_M, 1, 1)
  
  #2.
  halt #on last line
<code>

To succesfully run this code you will nedd to download esp32_ulp library from https://github.com/micropython/micropython-esp32-ulp 

The code, client() method is prepared for integration with ThingsBoard (https://thingsboard.io/)

To succesfully integrate then solution with ThingsBoard server you need to configure reed_setting.py file, especially all following fields

device_id = "thingsboard device acces token" </br>
LPlen = 15 #telemetry frequency in minutes</br>
channel = "LP15" # ThingsBoad telemetry name</br>
temp_sensor = "None" #type of temp sensor if attached to esp32</br>
tempPin = 12 #temp sensor pin</br>
wifiSSID = "your wifi name"</br>
wifiPWD = "wifi password"</br>
server="your thingsboard server IP"</br>
port="your thingsboad server port"</br>



