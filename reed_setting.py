device_id = "thingsboard device acces token"
LPlen = 15 #duration of telemetry interval in minutes
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
bat_measure = False # battery status (experimental) can be checked via pin 34 see the code for details
