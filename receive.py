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

# from time import time as get_time
from matplotlib.lines import Line2D
import numpy as np
import scipy.misc as smp
from sklearn.preprocessing import normalize
import mido

import matplotlib.pyplot as plt

import argparse

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

PATH = args.path
HOST = args.host

on_windows = os.name == "nt"

# sync files in the rpi directory
print("Syncing files to the raspberry pi")
subprocess.run(
    (["wsl"] if on_windows else [])
    + [
        "rsync",
        "-avz",
        "--delete",
        "--exclude",
        "__pycache__",
        "rpi/",
        f"{HOST}:{PATH}",
    ]
)

if args.install:
    print("Installing dependencies on the raspberry pi")
    # make sure rpi dependencies are installed
    subprocess.run(["ssh", HOST, f"cd {PATH}; ./setup_rpi.sh"])

print("Running the script on the raspberry pi")
process_on_rpi = subprocess.Popen(
    [
        "ssh",
        HOST,
        f"cd {PATH}; $HOME/.local/bin/poetry run python3 print_ic2.py",
    ],
    bufsize=0,
    # text=True,
    stdout=subprocess.PIPE,
)


# Create a figure and axis
plt.ion()
stats_ax: plt.Axes
grid_ax: plt.Axes
fig, (grid_ax, stats_ax) = plt.subplots(1, 2)
fig.canvas.mpl_connect("close_event", lambda x: exit(0))  # listen to close event

MIN_TEMP = 0
MAX_TEMP = 37.5
TRIGGER_TEMP = 15
TRIGGER_FROM_MEAN = 3
TRIGGER_FROM_MIN = 3
MAX_VALUES = 50

# New Constants
WINDOW_SIZE = 10  # Number of samples to consider for moving average
HYSTERESIS = 0.05  # Minimum change required to update MIDI value
SMOOTHING_FACTOR = 0.2  # Exponential smoothing factor (0 to 1)

# Initialize variables
weighted_x_history = deque(maxlen=WINDOW_SIZE)
last_midi_value = 0
smoothed_value = 0

# Plot the grid using a colormap
im = grid_ax.imshow(
    [[0]], cmap="hot", vmin=MIN_TEMP, vmax=MAX_TEMP, interpolation="bicubic"
)
im2 = grid_ax.imshow([[0]], interpolation="nearest")


# Add a colorbar
cbar = grid_ax.figure.colorbar(im, ax=grid_ax)

stats_lines: list[Line2D] = []
stats_labels = [
    "Mean Intensity",
    "Standard Deviation",
    "Median",
    "Weighted X",
    "Weighted Y",
    "Min",
    "Max",
]
for i in range(len(stats_labels)):
    (line,) = stats_ax.plot([], [], label=stats_labels[i])
    stats_lines.append(line)

stats_ax.set_title("Stats")
stats_ax.set_xlabel("Time")
stats_ax.set_ylabel("Normalized Value")
stats_ax.legend()

stats_data = {label: [] for label in stats_labels}
stats_time = []


def weighted_center_of_mass(grid):
    """Calculates the weighted center of mass of a grid.

    Args:
      grid: A 2D numpy array representing the grid of values.

    Returns:
      A tuple representing the x and y coordinates of the center of mass.
    """

    # Ensure grid is a numpy array
    grid = np.array(grid)

    # Calculate total weight
    total_weight = np.sum(grid)

    # Calculate weighted coordinates
    x_weighted_sum = np.sum(np.multiply(grid, np.arange(grid.shape[1])))
    y_weighted_sum = np.sum(np.multiply(grid, np.arange(grid.shape[0])[:, np.newaxis]))

    # Calculate center of mass
    x_center = x_weighted_sum / total_weight
    y_center = y_weighted_sum / total_weight

    return x_center, y_center


newlines = ["\n", "\r\n", "\r"]


def unbuffered(proc: Popen, stream="stdout"):
    stream = getattr(proc, stream)
    with contextlib.closing(stream):
        while True:
            out = []
            last = stream.read(1)
            # Don't loop forever
            if last == "" and proc.poll() is not None:
                break
            while last not in newlines:
                # Don't loop forever
                if last == "" and proc.poll() is not None:
                    break
                out.append(last)
                last = stream.read(1)
            out = "".join(out)
            yield out


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


if on_windows:
    output_names = mido.get_output_names()
    print("Output names:", output_names)
    midi_out = mido.open_output(output_names[1])
else:
    mido.set_backend("mido.backends.portmidi")
    # os.set_blocking(p.stdout.fileno(), False)  # That's what you are looking for
    output_names = mido.get_output_names()
    print("Output names:", output_names)
    midi_out = mido.open_output(output_names[1])

print("Starting to read the output")
d = b""


cur_line = ""


def threaded_read():
    global cur_line
    while True:
        cur_line = process_on_rpi.stdout.readline().decode("utf-8")


def mapFromTo(x, a, b, c, d):
    y = (x - a) / (b - a) * (d - c) + c
    return max(c, min(d, y))


thread = Thread(target=threaded_read)
thread.start()

# start_time = get_time()
last_processed_line = ""

while True:
    if last_processed_line == cur_line:
        time.sleep(1 / 60)
        continue

    l = cur_line
    last_processed_line = l

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
    im.set_data(grid)

    mean_intensity = np.mean(grid)
    std_dev = np.std(grid)
    median_intensity = np.median(grid)
    weighted_x, weighted_y = weighted_center_of_mass(grid)
    min_temp = np.min(grid)
    max_temp = np.max(grid)

    # data_above_range = grid > (min + TRIGGER_FROM_MIN)
    data_above_range = grid > (mean_intensity + TRIGGER_FROM_MEAN)

    # VISUALISATION \/ \/

    # full blue if true, transparent if false
    data_above_range_color = np.zeros((*data_above_range.shape, 4))
    data_above_range_color[data_above_range] = [0, 0, 1, 0.5]

    im2.set_data(data_above_range_color)
    stats_data["Mean Intensity"].append(mean_intensity)
    stats_data["Standard Deviation"].append(std_dev)
    stats_data["Median"].append(median_intensity)
    stats_data["Weighted X"].append(weighted_x)
    stats_data["Weighted Y"].append(weighted_y)
    stats_data["Min"].append(min_temp)
    stats_data["Max"].append(max_temp)

    n_x = stats_data["Weighted X"][-1]
    midi_value = get_smooth_midi_value(n_x)
    human_detected = mapFromTo(max_temp, 7.0, 9.0, 0, 1)

    midi_out.send(
        mido.Message(
            "control_change",
            control=1,
            value=midi_value,
        )
    )

    midi_out.send(
        mido.Message(
            "control_change",
            control=2,
            value=int(human_detected * 127),
        )
    )

    print("Raw Weighted X:", n_x)
    print("Smoothed MIDI value:", midi_value)
    print(f"Human {human_detected}")

    stats_time.append(time.time())

    for i, line in enumerate(stats_lines):
        data = np.array(stats_data[stats_labels[i]])
        # data = data / np.sqrt(np.sum(data**2))
        line.set_xdata(stats_time)
        line.set_ydata(data)

    if len(stats_time) > MAX_VALUES:
        stats_time.pop(0)
        for label in stats_labels:
            stats_data[label].pop(0)

    stats_ax.relim()
    stats_ax.autoscale_view()

    # Show the plot
    fig.canvas.draw()
    plt.draw()
    fig.canvas.flush_events()

    # plt.pause(0.01)  # Add a small pause to allow time for plot updating
