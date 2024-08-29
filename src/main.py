import argparse

from src.graph import GraphController
from src.midi import MidiController
from rpi import RpiController
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
    "--ir-host",
    help="the hostname of the raspberry pi running the ir",
    default="edeetee@raspberrypi.local",
)

parser.add_argument(
    "--pir-host",
    help="the hostname of the raspberry pi with the PIR sensor",
    default="edeetee@sensorpi.local",
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
IR_HOST = args.ir_host
PIR_HOST = args.pir_host

rpi_comm_ir = RpiController(IR_HOST, PATH, args.install)
rpi_comm_pir = RpiController(PIR_HOST, PATH, args.install)

graph = GraphController()
stats = StatsController()
midi = MidiController()


while True:

    grid = rpi_comm_ir.get_ir_grid()
    pir_array = rpi_comm_pir.get_motion_array()

    if grid is None:
        continue

    stats.process_frame(grid)
    midi.process_frame(stats)
    graph.process_frame(grid, stats)
