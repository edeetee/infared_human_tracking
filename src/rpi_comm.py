import argparse
import os
import subprocess
from threading import Thread
import time


# start_time = get_time()


class RpiCommController:
    def __init__(self, args: argparse.Namespace):
        on_windows = os.name == "nt"

        PATH = args.path
        HOST = args.host

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

        self.cur_line = ""
        self.las_processed_line = self.cur_line

        def threaded_read():
            while True:
                self.cur_line = process_on_rpi.stdout.readline().decode("utf-8")

        print("Starting to read the output")
        thread = Thread(target=threaded_read)
        thread.start()

    # line if new line, else None
    def get_line(self):
        if self.last_processed_line == self.cur_line:
            time.sleep(1 / 60)
            return None

        self.last_processed_line = self.cur_line

        return self.cur_line


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
