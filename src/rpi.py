import argparse
import contextlib
import json
import os
import subprocess
from threading import Thread
import time
import numpy as np


class RpiController:
    def __init__(self, HOST: str, PATH: str, install: bool):
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

        if install:
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

        self.cur_line = ""
        self.las_processed_line = self.cur_line

        def threaded_read():
            while True:
                self.cur_line = process_on_rpi.stdout.readline().decode("utf-8")

        print("Starting to read the output")
        thread = Thread(target=threaded_read)
        thread.start()

    def get_motion_array(self) -> np.ndarray[bool]:
        l = self.get_new_line()

        if l is None:
            return None

        try:
            data = json.loads(l)
        except:
            print(l)
            time.sleep(1)
            return None

        # print(unpickled)
        grid = np.array(data)
        return grid

    def get_ir_grid(self, print_output=False) -> None | np.ndarray[float]:
        l = self.get_new_line()

        if l is None:
            return None

        try:
            data = json.loads(l)
        except:
            print(l)
            time.sleep(1)
            return None

        # print(unpickled)
        if print_output:
            for row in data:
                for cell in row:
                    print(f"{cell:.0f}", end=" ")
                print()
            print()

        grid = np.array(data)
        grid = np.rot90(grid, -1)

        return grid

    # line if new line, else None
    def get_new_line(self):
        if self.last_processed_line == self.cur_line:
            time.sleep(1 / 60)
            return None

        self.last_processed_line = self.cur_line

        return self.cur_line


newlines = ["\n", "\r\n", "\r"]


def unbuffered(proc: subprocess.Popen, stream="stdout"):
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
