# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import busio
import board
from scipy.interpolate import griddata
import adafruit_amg88xx
import json

i2c_bus = busio.I2C(board.SCL, board.SDA)

# initialize the sensor
sensor = adafruit_amg88xx.AMG88XX(i2c_bus)

# let the sensor initialize
time.sleep(0.1)

FPS = 60
PERIOD = 1 / FPS

while True:
    pixels = []
    pickled = json.dumps(sensor.pixels)
    print(
        pickled, flush=True
    )  # flush to make sure it's printed immediately, even in non-interactive mode
    time.sleep(PERIOD)
