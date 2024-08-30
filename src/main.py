import _thread
import gc
import socket
import time

import config
import esp32
import machine
import micropython
import uasyncio as asyncio
import urequests
from machine import ADC, RTC, Pin, SoftI2C

from lib import ahtx0, utils
from lib.class_display import DisplayInterface
from lib.class_wifi import Wifi
from lib.primitives.pushbutton import Pushbutton

micropython.mem_info()
micropython.qstr_info()
gc.enable()
# gc.collect()  # problem with the display

rtc = RTC()
dt = rtc.datetime()

gdata = {}
gdata["display_on"] = True
gdata["display_screen"] = "default"
gdata["display_refresh"] = 1
gdata["day"] = dt[0] + dt[1] + dt[2]
gdata["hour"] = dt[4] + dt[5]
gdata["printer_data"] = 0

# sensor_light = ADC(Pin(2))
# sensor_light.atten(ADC.ATTN_11DB)

battery = ADC(Pin(4))
battery.atten(ADC.ATTN_11DB)
gdata["batt"] = battery.read()
gdata["batt_bars"] = 4
gdata["batt_changed_status"] = True

try:
    i2c_ahtx = SoftI2C(scl=Pin(43), sda=Pin(44))
    sensor_temp = ahtx0.AHT20(i2c_ahtx)
    gdata["temp"] = sensor_temp.temperature
    gdata["umid"] = sensor_temp.relative_humidity
except Exception:
    gdata["temp"] = "-"
    gdata["umid"] = "-"

gdata["temp"] = "-"
gdata["umid"] = "-"

display = DisplayInterface()
wifi = Wifi()
gdata["wifi"] = wifi.status()
display.screen_default(gdata, clear=True)


def get_data_3dprinter():
    s = socket.socket()
    s.settimeout(1)
    try:
        s.connect(
            socket.getaddrinfo(config.IP_3D_PRINTER, 80, 0, socket.SOCK_STREAM)[0][-1]
        )
        s.close()
        data = urequests.get(
            f"http://{config.IP_3D_PRINTER}/printer/objects/query?print_stats&display_status"
        )
        if data.status_code == 200:
            gdata["printer_data"] = data.json()
    except Exception:
        gdata["printer_data"] = 0
        s.close()
        return 0
    return 0


def show_3d_printer_data():
    return 0


def every_5s(wait):
    while True:
        gc.collect()  # problem with the display
        if gdata["display_on"]:
            try:
                gdata["temp"] = sensor_temp.temperature
                gdata["umid"] = sensor_temp.relative_humidity
            except Exception:
                gdata["temp"] = "-"
                gdata["umid"] = "-"
            gdata["batt"] = battery.read()
            gdata["batt_porcent"] = utils.map(gdata["batt"], 220, 355, 0, 100)
            batt_bars = round(gdata["batt_porcent"] / 33)
            if gdata["batt_bars"] != batt_bars:
                gdata["batt_changed_status"] = True
                gdata["batt_bars"] = batt_bars
            else:
                gdata["batt_changed_status"] = False
            gdata["wifi"] = wifi.status()
            get_data_3dprinter()
        time.sleep(wait)


_thread.start_new_thread(every_5s, (5,))


def timecron_action(action="play"):
    if action == "play":
        if gdata["timecron"]["status"] == "play":
            gdata["timecron"]["status"] = "pause"
        else:
            gdata["timecron"]["status"] = "play"
        gdata["timecron"]["cron_start"] = time.time()
    elif action == "pause":
        gdata["timecron"]["status"] = "pause"
    elif action == "stop":
        gdata["timecron"]["status"] = "stop"


pin0 = Pin(0, mode=Pin.IN, pull=Pin.PULL_UP)
button0 = Pushbutton(pin0, suppress=True)
pin14 = Pin(14, Pin.IN, Pin.PULL_UP)
button14 = Pushbutton(pin14, suppress=True)

button14.release_func(display.screen_switch, (gdata,))
button14.double_func(display.screen_default, (gdata,))
button14.long_func(display.power_switch, (gdata,))

button0.release_func(timecron_action, ("play",))
button0.double_func(timecron_action, ("pause",))
button0.long_func(timecron_action, ("stop",))


async def main():
    while True:
        dt = rtc.datetime()
        if gdata["display_on"]:
            if gdata["display_screen"] == "default":
                if dt[5] % 10 == 0 and dt[6] == 42:
                    machine.freq(240_000_000)
                    display.screen_default(gdata, clear=True)
                else:
                    machine.freq(160_000_000)
                    display.screen_default(gdata)
            elif gdata["display_screen"] == "timecron":
                display.screen_timecron(gdata)
            elif gdata["display_screen"] == "gps":
                display.screen_gps(gdata)
            elif gdata["display_screen"] == "info":
                display.screen_info(gdata)
        await asyncio.sleep(gdata["display_refresh"])


esp32.wake_on_ext0(
    pin=Pin(0, mode=Pin.IN, pull=Pin.PULL_UP), level=esp32.WAKEUP_ANY_HIGH
)

asyncio.run(main())
