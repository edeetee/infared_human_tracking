import codecs
import os
import subprocess
from subprocess import Popen, PIPE
import pickle
import json


HOST = "raspberrypi.local"
PATH = "/home/edeetee/rpi"

# Run the command

p = subprocess.Popen(
    [
        "ssh",
        HOST,
        f"cd {PATH}; DISPLAY=:0 /home/edeetee/.local/bin/poetry run python3 visualise_i2c.py",
    ],
    stdout=subprocess.PIPE,
)

while True:
    l = p.stdout.readline().decode("utf-8")

    # l = l.replace("\n", "")

    try:
        # pickled = l.decode()
        unpickled = json.loads(l)
        # unpickled = pickle.loads(l)
    except:
        print(l)
        continue

    # d = pickle.loads(l)

    # print(unpickled)
    for row in unpickled:
        for cell in row:
            print(f"{cell:.0f}", end=" ")

    print()
