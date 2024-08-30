import time

import st7789
from machine import RTC, Pin

from lib import JetBrains_105_numbers as font_numbers
from lib import UbuntuMono_20 as font2
from lib import UbuntuMono_70 as font4

from .utils import map

rtc = RTC()


class DisplayInterface:
    def __init__(self):
        self.tft = st7789.ST7789(
            Pin(48, Pin.OUT),
            Pin(47, Pin.OUT),
            Pin(46, Pin.OUT),
            Pin(45, Pin.OUT),
            Pin(42, Pin.OUT),
            Pin(41, Pin.OUT),
            Pin(40, Pin.OUT),
            Pin(39, Pin.OUT),
            Pin(8, Pin.OUT),
            Pin(9, Pin.OUT),
            170,
            320,
            reset=Pin(5, Pin.OUT),
            cs=Pin(6, Pin.OUT),
            dc=Pin(7, Pin.OUT),
            backlight=Pin(38, Pin.OUT),
            rotation=1,
            options=0,
            buffer_size=0,
        )
        self.tft.init()
        # self.tftled = PWM(Pin(38), freq=40_000_000, duty=1023)
        # self.tftled.duty(1023)
        self.bg = [1, 2, 3, 4]
        self.bg[0] = st7789.color565(5, 5, 5)
        self.bg[1] = st7789.color565(10, 10, 20)
        self.bg[2] = st7789.color565(15, 25, 15)
        self.bg[3] = st7789.color565(40, 20, 20)
        self.color_inactive = st7789.color565(100, 100, 100)
        self.color_inactivemax = st7789.color565(60, 60, 60)
        self.color_active = st7789.color565(180, 180, 180)
        self.color_activemax = st7789.WHITE
        self.color_black = st7789.BLACK
        self.clear()

    # def brightness(self, value):
    #     self.tftled.duty(value)  # 170 - 511

    # def brightness_change(self):
    #     steps = [170, 510, 1023]
    #     actual = self.tftled.duty()
    #     step_actual = 0 if actual == 1023 else steps.index(actual) + 1
    #     self.tftled.duty(steps[step_actual])

    def _datetime_setted(self):
        return False if rtc.datetime()[0] < 2020 else True

    def systray_battery(self, gdata, x=283, y=6):
        # if gdata["batt_changed_status"]:
        self.tft.rect(x - 2, y - 2, 35, 16, st7789.GREEN)
        self.tft.fill_rect(x + 33, y + 2, 3, 7, st7789.GREEN)
        color_bars = st7789.GREEN if gdata["batt_bars"] >= 1 else st7789.RED
        self.tft.fill_rect(x, y, 31, 12, st7789.BLACK)
        for i in range(gdata["batt_bars"] + 1):
            self.tft.fill_rect(283 + (i * 8), 6, 6, 12, color_bars)
            # gdata["batt_changed_status"] = False

    def systray_wifi(self, gdata, x=255, y=4):
        self.tft.hline(x, y, 16, self.color_inactive)
        self.tft.hline(x + 2, y + 3, 12, self.color_inactive)
        self.tft.hline(x + 4, y + 6, 8, self.color_inactive)
        self.tft.hline(x + 6, y + 9, 4, self.color_inactive)
        self.tft.hline(x + 7, y + 12, 2, self.color_inactive)
        self.tft.fill_rect(x + 7, y + 12, 2, 2, self.color_inactive)

        if gdata["connected"]:
            if gdata["quality"] > 85:
                self.tft.hline(x, y, 16, st7789.GREEN)
            if gdata["quality"] > 65:
                self.tft.hline(x + 2, y + 3, 12, st7789.GREEN)
            if gdata["quality"] > 45:
                self.tft.hline(x + 4, y + 6, 8, st7789.GREEN)
            if gdata["quality"] > 25:
                self.tft.hline(x + 6, y + 9, 4, st7789.GREEN)
            if gdata["quality"] != 0:
                self.tft.fill_rect(x + 7, y + 12, 2, 2, st7789.GREEN)

    def systray_bluetooth_logo(self, color=st7789.GREEN, x=237, y=3):
        self.tft.line(x, y, x + 6, y + 4, color)
        self.tft.line(x - 4, y + 4, x + 6, y + 13, color)
        self.tft.vline(x, y, 17, color)
        self.tft.line(x, y + 17, x + 6, y + 13, color)
        self.tft.line(x - 4, y + 13, x + 6, y + 4, color)

    def systray_bluetooth(self, status=0):
        if status == 0:  # Desativado
            self.systray_bluetooth_logo(self.color_inactive)
        elif status == 1:  # Disponivel
            self.systray_bluetooth_logo(st7789.GREEN)
        elif status == 2:  # Conetando...
            self.systray_bluetooth_logo(st7789.WHITE)
        elif status == 3:  # Conectado
            self.systray_bluetooth_logo(st7789.BLUE)

    def systray_data(self, hour=False):
        dt = rtc.datetime()
        if hour:
            self.tft.write(
                font2, f"{dt[4]:02d}:{dt[5]:02d}:{dt[6]:02d}", 2, 2, self.color_active
            )
        else:
            self.tft.write(
                font2, f"{dt[2]:02d}/{dt[1]:02d}/{dt[0]:04}", 2, 2, self.color_active
            )
            # weekday = ["M", "T", "W", "T", "F", "S", "S"]  # English
            weekday = ["S", "T", "Q", "Q", "S", "S", "D"]  # Portugues
            # weekday = ['L', 'M', 'M', 'G', 'V', 'S', 'D'] # Italiano
            col = 115
            for index, dw in enumerate(weekday):
                color = (
                    self.color_inactive if index != int(dt[3]) else self.color_active
                )
                self.tft.write(font2, dw, col, 2, color)
                col += 14

    def lateral_bar(self, selected=0):
        height = 30
        for i in range(4):
            color_n = self.color_activemax if selected == i else self.color_inactive
            self.tft.fill_rect(319, height, 1, 30, color_n)
            height += 35

    def screen_default(self, gdata, clear=False, only_hour=False):
        dt = rtc.datetime()
        if gdata["display_screen"] != "default" or clear:
            self.clear()
            self.tft.fill_circle(160, 66, 11, st7789.WHITE)
            self.tft.fill_circle(160, 108, 11, st7789.WHITE)
            self.lateral_bar()
        if (
            gdata["hour"] != dt[4] + dt[5]
            or gdata["display_screen"] != "default"
            or clear
        ):
            self.tft.write(font_numbers, f"{dt[4]:02d}", 10, 50, st7789.WHITE)
            self.tft.write(font_numbers, f"{dt[5]:02d} ", 186, 50, st7789.WHITE)
        if (
            gdata["day"] != dt[0] + dt[1] + dt[2]
            or gdata["display_screen"] != "default"
            or clear
        ):
            self.systray_data()
        gdata["display_screen"] = "default"
        self.systray_bluetooth()
        self.systray_wifi(gdata["wifi"])
        self.systray_battery(gdata)
        sec = f"{dt[6]:02d}"
        self.tft.write(font2, sec[0], 155, 56, st7789.BLACK, st7789.WHITE)
        self.tft.write(font2, sec[1], 155, 98, st7789.BLACK, st7789.WHITE)
        gdata["day"] = dt[0] + dt[1] + dt[2]
        gdata["hour"] = dt[4] + dt[5]
        temperature = humidity = "-"
        if gdata["umid"] != "-":
            humidity = f"{gdata['umid']:.0f}%"
        if gdata["temp"] != "-":
            temperature = f"{gdata['temp']:.0f}°"
        self.tft.write(font2, humidity, 276, 144, self.color_active)
        self.tft.write(font2, temperature, 210, 144, self.color_active)
        self.printer_status(gdata)

    def printer_status(self, gdata):
        if gdata["printer_data"] == 0:
            self.icon_printer(0)
            self.tft.fill_rect(40, 146, 160, 16, st7789.BLACK)
        else:
            self.icon_printer(1)
            status = gdata["printer_data"]["result"]["status"]
            if status["print_stats"]["state"] == "printing":
                progress = status["display_status"]["progress"]
                progress = progress * 100
                self.tft.rect(40, 146, 160, 16, self.color_inactivemax)
                self.tft.fill_rect(42, 148, 156, 12, self.color_inactive)
                val = map(progress, 0, 100, 0, 156)
                self.tft.fill_rect(42, 148, int(val), 12, self.color_active)
            else:
                self.tft.fill_rect(40, 146, 160, 16, st7789.BLACK)

    def icon_printer(self, status=0, x=10, y=145):
        color1 = self.color_inactive if status == 0 else st7789.GREEN
        color2 = self.color_active if status != 0 else st7789.BLACK
        self.tft.fill_rect(x + 1, y, 14, 10, color1)
        self.tft.rect(x, y + 5, 16, 6, color1)
        self.tft.hline(x + 6, y + 4, 8, color2)
        self.tft.hline(x + 2, y + 10, 12, color2)
        for i in range(1, 7):
            self.tft.hline(x + 1 + i, y + 10 + i, 14 - (i * 2), color1)

    def screen_timecron(self, gdata, clear=False):
        dt = rtc.datetime()
        if gdata["display_screen"] != "timecron":
            self.clear()
            self.lateral_bar(1)
        self.systray_data(hour=True)
        self.systray_bluetooth()
        self.systray_wifi(gdata["wifi"])
        self.systray_battery(gdata)
        gdata["display_screen"] = "timecron"
        if gdata["timecron"]["status"] == "stop":
            self.tft.write(font4, "00:00.00", 10, 60, self.color_activemax)
        elif gdata["timecron"]["status"] == "play":
            dt = time.localtime(time.time() - gdata["timecron"]["cron_start"])
            dt = f"{dt[4]:02d}:{dt[5]:02d}."
            dt_ms = f"{rtc.datetime()[7]}"[:2]
            gdata["timecron"]["time_paused"] = dt + dt_ms
            self.tft.write(font4, dt + dt_ms, 10, 60, st7789.GREEN)
        elif gdata["timecron"]["status"] == "pause":
            self.tft.write(
                font4, gdata["timecron"]["time_paused"], 10, 60, st7789.GREEN
            )

    def screen_gps(self, gdata):
        dt = rtc.datetime()
        if gdata["display_screen"] != "gps":
            self.clear()
            self.lateral_bar(2)
        self.systray_data(hour=True)
        self.systray_bluetooth()
        self.systray_wifi(gdata["wifi"])
        self.systray_battery(gdata)
        gdata["display_screen"] = "gps"
        self.tft.write(
            font2, f"Hour: {dt[4]:02d}:{dt[5]:02d}", 30, 29, st7789.GREEN, self.bg[1]
        )
        self.tft.write(font2, "Temp: 28c", 30, 29, st7789.GREEN, self.bg[1])
        self.tft.write(font2, "Humi: 43%", 30, 53, st7789.GREEN, self.bg[1])
        self.tft.write(
            font2, "Wifi: {:02d}dbm".format(50), 30, 78, st7789.GREEN, self.bg[1]
        )
        self.tft.write(font2, "Batt: 97%", 30, 103, st7789.GREEN, self.bg[1])

    def screen_info(self, gdata):
        if gdata["display_screen"] != "info":
            self.clear()
            self.lateral_bar(3)
        self.systray_data(hour=True)
        self.systray_bluetooth()
        self.systray_wifi(gdata["wifi"])
        self.systray_battery(gdata)
        gdata["display_screen"] = "info"

    def screen_on(self, gdata):
        print("Display ON")
        gdata["display_on"] = True
        # machine.freq(240_000_000)
        self.tft.on()

    def screen_off(self, gdata):
        print("Display OFF")
        gdata["display_on"] = False
        # machine.freq(80_000_000)
        self.tft.off()

    def screen_switch(self, gdata):
        if gdata["display_screen"] == "default":
            gdata["display_refresh"] = 0.1
            # machine.freq(240_000_000)
            gdata["batt_changed_status"] = True
            gdata["timecron"] = {}
            gdata["timecron"]["type"] = "cron"
            gdata["timecron"]["status"] = "stop"
            gdata["timecron"]["cron_start"] = 0
            gdata["timecron"]["cron_pause"] = 0
            self.screen_timecron(gdata)
        elif gdata["display_screen"] == "timecron":
            # machine.freq(160_000_000)
            gdata["batt_changed_status"] = True
            gdata["display_refresh"] = 1
            self.screen_gps(gdata)
        elif gdata["display_screen"] == "gps":
            # machine.freq(160_000_000)
            gdata["batt_changed_status"] = True
            gdata["display_refresh"] = 1
            self.screen_info(gdata)
        elif gdata["display_screen"] == "info":
            # machine.freq(160_000_000)
            gdata["display_refresh"] = 1
            gdata["batt_changed_status"] = True
            self.screen_default(gdata)

    def clear(self):
        self.tft.fill(st7789.BLACK)

    def jpg(self, image, x=0, y=0):
        self.tft.jpg(image, x, y)

    def png(self, image, x=0, y=0):
        self.tft.png(image, x, y)

    def power_switch(self, gdata):
        self.screen_off(gdata) if gdata["display_on"] else self.screen_on(gdata)
        time.sleep(0.5)


class Button(DisplayInterface):
    def __init__(self):
        pass

    def function1(self, gdata):
        if gdata["display_screen"] == "default":
            print("I'm in Default Display")
            return True
        if gdata["display_screen"] == "timecron":
            print("I'm in Time Cron")
            return True
        if gdata["display_screen"] == "gps":
            print("I'm in GPS")
            return True
        if gdata["display_screen"] == "info":
            print("I'm in Info Display")
            return True
