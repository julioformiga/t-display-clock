import time

import network

import config


def map(x, in_min, in_max, out_min, out_max, type="intmax"):
    if type == "float":
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    elif type == "int":
        return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min
    else:
        return max(
            min(
                out_max,
                (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min,
            ),
            out_min,
        )


def battery_display(tft, battery_read):
    x_init = 104

    tft.draw_rectangle(x_init - 2, 3, 20, 9, tft.WHITE)
    tft.draw_rectangle(x_init + 18, 4, 2, 6, tft.WHITE)
    tft.fill_rectangle(x_init, 5, 16, 5, tft.BLACK)

    if battery_read < 1500:
        tft.fill_rectangle(x_init, 5, 16, 5, tft.WHITE)
    elif battery_read > 2420:
        tft.fill_rectangle(x_init, 5, 16, 5, tft.BLUE)
    else:
        battery_percent = map(battery_read, 1870, 2380, 0, 100)
        color = tft.GREEN if battery_percent > 30 else tft.RED
        tft.fill_rectangle(x_init, 5, map(battery_percent, 0, 100, 0, 16), 5, color)

    # tft.rect(x_init - 2, 3, 20, 9, tft.WHITE)
    # tft.rect(x_init + 18, 4, 2, 6, tft.WHITE)
    # tft.fill_rect(x_init, 5, 16, 5, tft.BLACK)
    # color = tft.GREEN if battery_percent > 30 else tft.RED
    # tft.fill_rect(x_init, 5, map(battery_percent, 0, 100, 0, 16, 5), 5, color)


def read_sensor(sensor):
    # global temp, hum
    temp = hum = 0
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        if (isinstance(temp, float) and isinstance(hum, float)) or (
            isinstance(temp, int) and isinstance(hum, int)
        ):
            # uncomment for Fahrenheit
            # temp = temp * (9/5) + 32.0
            hum = round(hum, 2)
            return {"temp": temp, "hum": hum}
        else:
            return {"error": "Invalid sensor readings"}
    except OSError as e:
        print(e)
        return {"error": e}


def dbm2porcentage(dbm):
    if dbm <= -100:
        netquality = 0
    elif dbm >= -50:
        netquality = 100
    else:
        netquality = 2 * (dbm + 100)
    return netquality


def do_connect():
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        wlan.active(True)
        wlan.connect(config.WIFI_SSID, config.WIFI_PASS)
        print("Conneting...")
        while not wlan.isconnected():
            pass
        print("Connected")
        status = wlan.ifconfig()
        print("IP = " + status[0])
    netip = wlan.ifconfig()
    netdbm = wlan.status("rssi")
    netquality = dbm2porcentage(netdbm)

    return {"ip": netip[0], "dbm": netdbm, "quality": netquality}


def micropythonlogo(display, size=128):
    for size in range(2, size, 2):
        ix = (display.tft.width() - size) / 2
        iy = (display.tft.height() - size) / 2
        display.tft.fill_rect(
            2 + int(ix), 2 + int(iy), size - 4, size - 4, display.color_activemax
        )
        time.sleep(0.005)

    if size < 48:
        line = 1
    elif size < 64:
        line = 2
    else:
        line = 3
    color = display.color_black
    display.tft.fill_rect(
        int((size / 3.5) + ix - 1),
        int((size / 4) + iy),
        line,
        int(size / 1.4) + 2,
        color,
    )
    display.tft.fill_rect(
        int((size / 2) + ix - 1),
        int((size / 16) + iy - 4),
        line,
        int(size / 1.4 + 2),
        color,
    )
    display.tft.fill_rect(
        int((size / 1.4) + ix - 1),
        int((size / 4) + iy),
        line,
        int((size / 1.4) + 2),
        color,
    )

    display.tft.fill_rect(
        int((size / 1.2) + ix),
        int((size / 1.3) + iy),
        int(size / 16),
        int(size / 8),
        color,
    )
    time.sleep(1)
    display.clear()
