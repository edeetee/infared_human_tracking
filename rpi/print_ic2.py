# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import argparse
import socket
import time
import busio
import board
from scipy.interpolate import griddata
import adafruit_amg88xx
import json

parser = argparse.ArgumentParser()
parser.add_argument(
    "--port",
    help="port of the server",
)

args = parser.parse_args()

BIND_HOST = "0.0.0.0"
PORT = int(args.port)

print(f"Binding to {BIND_HOST}:{PORT}")

i2c_bus = busio.I2C(board.SCL, board.SDA)

# initialize the sensor
sensor = adafruit_amg88xx.AMG88XX(i2c_bus)

# let the sensor initialize
time.sleep(0.1)

FPS = 60
PERIOD = 1 / FPS

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    # sock.bind((BIND_HOST, PORT))
    # sock.listen()
    while True:
        # (proxy_socket, proxy_address) = sock.accept()
        # while True:
        pixels = []
        pickled = json.dumps(sensor.pixels)
        # print(
        #     pickled, flush=True
        # )  # flush to make sure it's printed immediately, even in non-interactive mode
        proxy_socket.send(pickled.encode())
        time.sleep(PERIOD)
