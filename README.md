# ESP32-PulseMeter
This repository contains quick and dirty Micropython ESP32 Pulse Sensor implementation, which can be used to colect your water and gas meter pulses and calulate 15 minutes consumption. The usage of ULP makes this code usable for battery only solutions. The ULP code counts pulses on **RTC_GPIO10** (io_number variable in ULP code) pin - check your ESP chip's datasheet to locate it properly.

Futher details are documented on WIKI page https://github.com/jpajzinka/ESP32-PulseMeter/wiki.

# ULP integration in Micropython

To implement a pulse sensor in micropython is fairly simple - however the trick is to make a batery effective solution, where in my case the ULP code is the key. The ULP code as such is inspired by code found on this forum https://esp32.com/viewtopic.php?t=13638 

To succesfully run this code you will nedd to download esp32_ulp library from https://github.com/micropython/micropython-esp32-ulp 

The code, is designed for integration with ThingsBoard (https://thingsboard.io/), you can modify the code() function to integrate with alternative servers.

# Making it work

First you need to flash micropython on your ESP32 board (make sure board has ULP). Follow these instructions https://docs.micropython.org/en/latest/esp32/tutorial/intro.html

Then you need to clone my repository and micropython-esp32-ulp repository.

Modify reed-setting.py file.


Start rshell copy necessary files to /pyboard

Start repl and import main

```
#Here are few key commands -you'll need to customize them, also don't forget to modify reed-setting.py file

esptool.py --port /dev/ttyUSB0 erase_flash
esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 esp32-20180511-v1.9.4.bin

git clone https://github.com/jpajzinka/ESP32-PulseMeter.git
git clone https://github.com/micropython/micropython-esp32-ulp.git

rshell -d /dev/ttyUSB0
cp micropython-esp32-ulp/esp32_ulp /pyboard/.
cp ESP32-PulseMeter/ulp-reed.py /pyboard/main.py
cp ESP32-PulseMeter/reed-setting.py /pyboard/.

repl
import main
```

# Configuration

To succesfully integrate then solution with ThingsBoard server you need to configure reed_setting.py file, especially all following fields:
```
device_id = "thingsboard device acces token"
LPlen = 15 #telemetry frequency in minutes
channel = "LP15" # ThingsBoad telemetry name
temp_sensor = "None" #type of temp sensor if attached to esp32
tempPin = 12 #temp sensor pin
wifiSSID = "your wifi name"
wifiPWD = "wifi password"
server="your thingsboard server IP"
port="your thingsboad server port"
bat_measure = False # battery status (experimental) can be checked via pin 34 see the code for details
```

# Scheme

![Lolin 32](https://github.com/jpajzinka/ESP32-PulseMeter/blob/main/images/fritzing_img.png)
