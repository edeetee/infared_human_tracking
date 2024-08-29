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
midi = MidiController()

while True:

    grid = rpi_comm.get_grid()

    if grid is None:
        continue

    stats.process_frame(grid)
    midi.process_frame(stats)
    graph.process_frame(grid, stats)
