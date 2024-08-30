import json
import os
import time
from typing import TypedDict
import numpy as np
import serial


class ArduinoResponse(TypedDict):
    ir_grid: np.ndarray[float]
    pir_array: np.ndarray[bool]


on_windows = os.name == "nt"

SERIAL_PORT = "/dev/cu.usbmodem11101"
if on_windows:
    SERIAL_PORT = "COM3"

BAUD = 1000000


class ArduinoController:
    def __init__(self):
        self.arduino = serial.Serial(SERIAL_PORT, BAUD, timeout=1)
        # wait for init
        # time.sleep(1)

    def read(self) -> None | ArduinoResponse:
        # tell arduino to send a message
        self.arduino.write(b"1")
        # self.arduino.flush()

        line = self.arduino.readline()

        try:
            data = json.loads(line)
        except:
            # time.sleep(1)
            return None

        # print(data)

        pir = np.array(data["pir"])

        ir_array = np.array(data["ir"])
        ir_grid = ir_array.reshape((8, 8))

        return ArduinoResponse(ir_grid=ir_grid, pir_array=pir)
