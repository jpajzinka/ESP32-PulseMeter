import machine, time
import onewire, ds18x20
import reed_setting as setting
import esp32
import uio, ure, utime, urequests
import network, socket
import sys
from esp32 import ULP
from machine import Pin, mem32, ADC
from esp32_ulp import src_to_binary
import json

#the ulp source code is ULP pulse counter working on pin 0, improved copy of code from here https://esp32.com/viewtopic.php?t=13638
source = """\
#define DR_REG_RTCIO_BASE            0x3ff48400
#define RTC_IO_TOUCH_PAD0_REG        (DR_REG_RTCIO_BASE + 0x94)
#define RTC_IO_TOUCH_PAD0_MUX_SEL_M  (BIT(19))
#define RTC_IO_TOUCH_PAD0_FUN_IE_M   (BIT(13))
#define RTC_GPIO_IN_REG              (DR_REG_RTCIO_BASE + 0x24)
#define RTC_GPIO_IN_NEXT_S           14
  
  /* Define variables, which go into .bss section (zero-initialized data) 
  .bss*/

  /* Next input signal edge expected: 0 (negative) or 1 (positive) */
  .global next_edge
next_edge:
  .long 0

  /* Total number of signal edges acquired */
  .global edge_count
edge_count:
  .long 0

  /* RTC IO number used to sample the input signal. Set by main program. */
  .global io_number
io_number:
  .long 10

  /* Code goes into .text section */
  .text
  .global entry
entry:
  # connect GPIO to the RTC subsystem so the ULP can read it
  WRITE_RTC_REG(RTC_IO_TOUCH_PAD0_REG, RTC_IO_TOUCH_PAD0_MUX_SEL_M, 1, 1)

  # switch the GPIO into input mode
  WRITE_RTC_REG(RTC_IO_TOUCH_PAD0_REG, RTC_IO_TOUCH_PAD0_FUN_IE_M, 1, 1)
  /* Load io_number */
  move r3, io_number
  ld r3, r3, 0

  /* Lower 16 IOs and higher need to be handled separately,
   * because r0-r3 registers are 16 bit wide.
   * Check which IO this is.
   */
  move r0, r3
  jumpr read_io_high, 16, ge

  /* Read the value of lower 16 RTC IOs into R0 */
  READ_RTC_REG(RTC_GPIO_IN_REG, RTC_GPIO_IN_NEXT_S, 16)
  rsh r0, r0, r3
  jump read_done

  /* Read the value of RTC IOs 16-17, into R0 */
read_io_high:
  READ_RTC_REG(RTC_GPIO_IN_REG, RTC_GPIO_IN_NEXT_S + 16, 2)
  sub r3, r3, 16
  rsh r0, r0, r3

read_done:
  and r0, r0, 1
  /* State of input changed? */
  move r3, next_edge
  ld r3, r3, 0
  add r3, r0, r3
  and r3, r3, 1
  jump edge_detected, eq
  /* Not changed */
  jump entry

  .global edge_detected
edge_detected:
  /* Flip next_edge */
  move r3, next_edge
  ld r2, r3, 0
  add r2, r2, 1
  and r2, r2, 1
  st r2, r3, 0
  /* Increment edge_count */
  move r3, edge_count
  ld r2, r3, 0
  add r2, r2, 1
  st r2, r3, 0
  halt
"""

logfile = uio.open("log.txt","a")
load_addr, entry_addr = 0, 3*4
ULP_MEM_BASE = 0x50000000
ULP_DATA_MASK = 0xffff  # ULP data is only in lower 16 bits
led = machine.Pin(5, machine.Pin.OUT)
led.value(1)

def blink(value=1):
    """
    The led blink is used to understand whats is happening with board
    1 blink - ulp initialized
    2 blinks - wifi init success 
    3 blinks - data sent to server
    It can be eliminated to save batery live
    """
    for i in range(0, value):
        led.value(0)
        time.sleep(0.3)
        led.value(1)
        time.sleep(0.3)

def log(msg="None", level=1):
    """
    This is log level which helps debuging of board connected via rhell or standalone one
    """
    timeNow= time.localtime()
    dateTime = "{:0>4d}-{:0>2d}-{:0>2d} {:0>2d}:{:0>2d}:{:0>2d}".format(timeNow[0], timeNow[1], timeNow[2], timeNow[3], timeNow[4], timeNow[5])
    message = "{} : {}".format(dateTime, msg)
    print(message)
    if level >=3:
        logfile.write(message+"\n")
        logfile.flush()

def value(start=0):
    """
    """
    val = (int(hex(mem32[ULP_MEM_BASE + start*4] & ULP_DATA_MASK),16))
    log("Reading value: " + str(val))
    return val

def init_ulp():
    binary = src_to_binary(source)
    ulp = ULP()
    ulp.set_wakeup_period(0, 50000)  # use timer0, wakeup after 50.000 cycles
    ulp.load_binary(load_addr, binary)
    ulp.run(entry_addr)
    log("ULP Started")

def setval(start=1, value=0x0):
    mem32[ULP_MEM_BASE + start*4] = value

def getTemp():
    
    data = {}
    if setting.temp_sensor == "DHT11" or setting.temp_sensor=="DHT22":

        import dht
        sensor = None
        if setting.temp_sensor == "DHT11":
            sensor = dht.DHT11(machine.Pin(setting.tempPin))
        elif setting.temp_sensor=="DHT22":
            sensor = dht.DHT22(machine.Pin(setting.tempPin))
        sensor.measure()
        t = sensor.temperature()
        h = sensor.humidity()
        if t > setting.threshold:
            log("Temperature too high - return")
            return

        data["Temperature"] = "{:3.1f}".format(t)
        data["Humidity"] = "{:3.1f}".format(h)

    elif setting.temp_sensor == "DS18X20":
        
        import onewire, ds18x20
        ds_pin = machine.Pin(setting.tempPin)
        ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
        roms = ds_sensor.scan()
        ds_sensor.convert_temp()
        t = ds_sensor.read_temp(roms[0])
        if t > setting.threshold:
            log("Temperature too high {} - return".format(t),3)
            return
 
        data["Temperature"] = {"now":"{:3.1f}".format(t) }
    
    elif setting.temp_sensor == "dummy":
        data["Temperature"] = {"now":"{:3.1f}".format(33.3) }
        data["Humidity"] = {"now":"{:3.1f}".format(33.3) }
    return data
    
def setupWifi():
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(0)
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        log("Disconnected")
        sta_if.active(1)
        sta_if.connect(setting.wifiSSID,setting.wifiPWD)
        while not sta_if.isconnected():
            pass
    log(sta_if.ifconfig())

def parseTime( response):
    #Parse time actualy calculates sleep time base on time from server HTTP response
    search = ure.compile("(\d\d):(\d\d):(\d\d)")
    log(response)
    match = ure.search(search, response)
    if match:
        mins = int(match.group(2) )
        secs = int(match.group(3) )
        log(str(mins)+" " +str(secs)) 
        return ( (setting.LPlen*60) - (( mins * 60 + secs )  % (setting.LPlen*60) ) ) * 1000
    else:
        #Sleep 30 seconds in case of failure
        return 30000

def client():
    message = {}
    if setting.bat_measure:
        p = ADC(Pin(34))
        p.atten(ADC.ATTN_11DB)
        message["Voltage"] = "{:3.1f}".format(p.read()*1.7)
    log("Client start", 3)
    pulses = value(1)
    message[setting.channel] = pulses/2/100
    setval(1,0x0)

    temp = getTemp()
    message.update(temp)
    
    log(str(message), 3)

    js = json.dumps(message)
    js = str(js).replace('"','').replace("'","")
    log(str(js), 3)
    
    try:
        s = socket.socket()
        s.connect((setting.server, setting.port))
        post = 'POST /api/v1/'+setting.device_id+'/telemetry  HTTP/1.1\r\nHost: '+setting.server+':'+str(setting.port)+'\r\nUser-Agent: ESP32\r\nAccept:*/*\r\nConnection: close\r\nContent-Type: application/json\r\nContent-Length: '+str(len(str(js)))+'\r\n\r\n'+str(js)+'\r\n\r\n'
        log(post)

        s.sendall(bytes(post,'utf8'))
        response = ""
        log("Response\n")
        while True:
            resp = s.readline()
            if resp:
                response += str(resp.decode("utf-8"))
            else:
                break
        if resp:
            log(str(resp, 'utf8'))
        s.close()

    except Exception as e:
        log("Exception:\n")
        sys.print_exception(e, logfile)
        logfile.flush()
        setval(1, pulses + value(1))
        machine.deepsleep(15*60*1000)
    
    return parseTime(response)

try:
    # The code logic itself
    log(machine.reset_cause(),3)
    #Init UlP
    if machine.reset_cause()==machine.PWRON_RESET or machine.reset_cause()==machine.HARD_RESET or machine.reset_cause()==machine.SOFT_RESET: 
        init_ulp()
        setval(1,0x0)
        blink(1)
    #Start wifi    
    setupWifi()
    blink(2)
    #run thingboard client, send data and sleep
    sleepTime = client()
    blink(3)
    log(sleepTime)
    machine.deepsleep(sleepTime)
    
except Exception as e:
    logfile = uio.open("log.txt","a")
    sys.print_exception(e)
    sys.print_exception(e, logfile)
    logfile.flush()
    machine.reset()
