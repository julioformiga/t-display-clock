import gc

import machine
import st7789
from machine import RTC

from lib import UbuntuMono_14 as font1
from lib.class_display import DisplayInterface
from lib.class_wifi import Wifi
from lib.utils import micropythonlogo

rtc = RTC()
# machine.freq(240_000_000)
machine.freq(160_000_000)
display = DisplayInterface()

micropythonlogo(display)
msg = "[OK] Frequency: {} Mhz".format(int(machine.freq() / 1000000))
print(msg)
display.tft.write(font1, msg, 2, 2, st7789.GREEN)

msg = "[OK] Memory: {0:.2f}kb".format(gc.mem_alloc() / 1024)
print(msg)
display.tft.write(font1, msg, 2, 22, st7789.GREEN)

if display._datetime_setted():
    msg = "[OK] {:02d}:{:02d} {:02d}/{:02d}/{}".format(
        rtc.datetime()[4],
        rtc.datetime()[5],
        rtc.datetime()[2],
        rtc.datetime()[1],
        rtc.datetime()[0],
    )
    print(msg)
    display.tft.write(font1, msg, 2, 42, st7789.GREEN)
    msg = "[DONE] Success!       "
    print(msg)
    display.tft.write(font1, msg, 2, 62, st7789.GREEN)
else:
    msg = "[FAIL] {:02d}:{:02d} {:02d}/{:02d}/{}".format(
        rtc.datetime()[4],
        rtc.datetime()[5],
        rtc.datetime()[2],
        rtc.datetime()[1],
        rtc.datetime()[0],
    )
    print(msg)
    display.tft.write(font1, msg, 2, 42, st7789.RED)
    # wait_seconds = 3
    msg = "[..] Initializing Wifi."
    # for i in range(wait_seconds):
    #     msg += "."
    #     print(f"\r{msg}", end="")
    #     display.tft.write(font1, msg, 2, 62, st7789.GREEN)
    #     time.sleep(1)
    # msg = "[OK] Wifi initialized           "
    print(f"\r{msg}")
    display.tft.write(font1, msg, 2, 62, st7789.GREEN)
    wifi = Wifi()
    ssid = wifi.status()["ssid"]
    msg = f"[..] Conneting to {ssid}"
    print(msg)
    display.tft.write(font1, msg, 2, 82, st7789.GREEN)
    if wifi.connect():
        if wifi.set_ntptime():
            msg = "[OK] {:02d}:{:02d} {:02d}/{:02d}/{}".format(
                rtc.datetime()[4],
                rtc.datetime()[5],
                rtc.datetime()[2],
                rtc.datetime()[1],
                rtc.datetime()[0],
            )
            print(msg)
            display.tft.write(font1, msg, 2, 102, st7789.GREEN)
            msg = "[DONE] Success!       "
            print(msg)
            display.tft.write(font1, msg, 2, 122, st7789.GREEN)
        else:
            msg = "[FAIL] {:02d}:{:02d} {:02d}/{:02d}/{}".format(
                rtc.datetime()[4],
                rtc.datetime()[5],
                rtc.datetime()[2],
                rtc.datetime()[1],
                rtc.datetime()[0],
            )
            print(msg)
            display.tft.write(font1, msg, 2, 102, st7789.RED)
            msg = "[DONE] Not connected!       "
            print(msg)
            display.tft.write(font1, msg, 2, 122, st7789.RED)
    else:
        print("Fail!")
display.tft.deinit()
