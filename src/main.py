import codecs
from collections import deque
import contextlib
import math
import os
import subprocess
from subprocess import Popen, PIPE
import pickle
import json
from threading import Thread
import time
import random

# from time import time as get_time
from matplotlib.lines import Line2D
import numpy as np
import scipy.misc as smp
from sklearn.preprocessing import normalize
import mido

import matplotlib.pyplot as plt

import argparse

from src.graph import GraphController
from src.midi import MidiController
from src.rpi_comm import RpiCommController
from src.stats import StatsController

# from PIL import Image

# Initialize parser
parser = argparse.ArgumentParser()
parser.add_argument(
    "--install",
    help="install dependencies on the raspberry pi",
    action="store_true",
)

parser.add_argument(
    "--host",
    help="the hostname of the raspberry pi",
    default="edeetee@raspberrypi.local",
)

parser.add_argument(
    "--path",
    help="the path on the raspberry pi",
    default="$HOME/rpi",
)

parser.add_argument(
    "--print-output",
    help="print the output of the script",
    action="store_true",
)


args = parser.parse_args()


rpi_comm = RpiCommController(args)
graph = GraphController()
stats = StatsController()


weighted_x_history = deque(maxlen=stats.WINDOW_SIZE)


# Smoothing constraig
WINDOW_SIZE = 10  # Number of samples to consider for moving average
HYSTERESIS = 0.05  # Minimum change required to update MIDI value
SMOOTHING_FACTOR = 0.2  # Exponential smoothing factor (0 to 1)


def get_smooth_midi_value(new_x):
    global last_midi_value, smoothed_value

    weighted_x_history.append(new_x)

    # Calculate moving average
    avg_x = sum(weighted_x_history) / len(weighted_x_history)

    # Apply exponential smoothing
    smoothed_value = (SMOOTHING_FACTOR * avg_x) + (
        (1 - SMOOTHING_FACTOR) * smoothed_value
    )

    # Normalize to 0-1 range, handling the case where all values are the same
    min_x = min(weighted_x_history)
    max_x = max(weighted_x_history)
    if max_x == min_x:
        normalized_value = 0.5  # Default to middle value if all inputs are the same
    else:
        normalized_value = (smoothed_value - min_x) / (max_x - min_x)

    # Ensure normalized_value is within [0, 1] range
    normalized_value = max(0, min(1, normalized_value))

    # Apply hysteresis
    new_midi_value = int(normalized_value * 127)
    if abs(new_midi_value - last_midi_value) > (HYSTERESIS * 127):
        last_midi_value = new_midi_value

    return last_midi_value


midi = MidiController()


def mapFromTo(x, a, b, c, d):
    y = (x - a) / (b - a) * (d - c) + c
    return max(c, min(d, y))


while True:

    l = rpi_comm.get_line()

    if l is None:
        continue

    try:
        data = json.loads(l)
    except:
        print(l)
        time.sleep(1)
        continue

    # print(unpickled)
    if args.print_output:
        for row in data:
            for cell in row:
                print(f"{cell:.0f}", end=" ")
            print()
        print()

    grid = np.array(data)
    grid = np.rot90(grid, -1)

    stats.process_frame(grid)

    n_x = stats.stats_data["Weighted X"][-1]
    midi_x_value = get_smooth_midi_value(n_x)
    human_detected = mapFromTo(stats.max_temp, 7.0, 9.0, 0, 1)

    midi.send(
        mido.Message(
            "control_change",
            control=1,
            value=midi_x_value,
        )
    )

    midi.send(
        mido.Message(
            "control_change",
            control=2,
            value=int(human_detected * 127),
        )
    )

    if random.random() < 0.1:  # 10% chance to send trigger
        note = 60  # MIDI note number for C3
        velocity = random.randint(64, 127)  # Random velocity between 64 and 127

        midi.send(mido.Message("note_on", note=note, velocity=velocity))
        print(f"Note On: C3 (note {note}) with velocity {velocity}")

        time.sleep(0.05)  # Hold the note for 100ms

        midi.send(mido.Message("note_off", note=note))
        print(f"Note Off: C3 (note {note})")

    print("Raw Weighted X:", n_x)
    print("Smoothed MIDI value:", midi_x_value)
    print(f"Human {human_detected}")
