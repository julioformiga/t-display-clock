import time

import network
import ntptime
from machine import RTC

import config


class Wifi:
    def __init__(self):
        self.wlan = network.WLAN(network.STA_IF)

    def _dbm2porcentage(self, dbm):
        if dbm <= -100:
            return 0
        if dbm >= -50:
            return 100
        return 2 * (dbm + 100)

    def set_ntptime(self, timezone=2):
        print("Setting time...")
        try:
            ntptime.settime()
            time.sleep(1)
            timezone = timezone * 60 * 60
            tm = time.localtime(time.time() + timezone)
            RTC().datetime((tm[0], tm[1], tm[2], tm[6], tm[3], tm[4], tm[5], 0))
            print("\rTime seted!")
            return True
        except OSError as err:
            print("\rFail to set time!")
            print(err)
            return False

    def status(self):
        if self.wlan.isconnected():
            netip = self.wlan.ifconfig()
            netdbm = self.wlan.status("rssi")
            netquality = self._dbm2porcentage(netdbm)
            return {
                "ssid": config.WIFI_SSID,
                "connected": True,
                "ip": netip[0],
                "dbm": netdbm,
                "quality": netquality,
            }
        return {"ssid": config.WIFI_SSID, "connected": False}

    def connect(self):
        if not self.wlan.isconnected():
            try:
                print("Conneting...")
                self.wlan.active(False)
                self.wlan.active(True)
                self.wlan.connect(config.WIFI_SSID, config.WIFI_PASS)
                self.wlan.config(hostname=config.HOSTNAME)
                tryconnect = 1
                print(f"Trying {config.WIFI_SSID}...")
                while not self.wlan.isconnected():
                    print(f"\r#{tryconnect}", end="")
                    time.sleep(0.01)
                    tryconnect += 1
                del tryconnect
                print()
            except OSError as err:
                print(err)
                self.connect()
        if self.wlan.isconnected():
            print("Connected IP:", self.status()["ip"])
            return True
        else:
            print("Fail to connect.")
            return False

    def disconnect(self):
        if self.wlan.isconnected():
            self.wlan.disconnect()
            self.wlan.active(False)
            print("Disconnected")
        return self.status()

    def switch(self):
        if self.wlan.isconnected():
            self.disconnect()
        else:
            self.connect()
            self.set_ntptime()
