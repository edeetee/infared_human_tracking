import argparse

from src.arduino import ArduinoController
from src.graph import GraphController
from src.midi import MidiController
from src.stats import StatsController

graph = GraphController()
stats = StatsController()
midi = MidiController()
arduino = ArduinoController()

while True:

    data = arduino.read()

    if data is None:
        continue

    grid = data["ir_grid"]
    pir_array = data["pir_array"]

    if pir_array.any():
        print("Motion detected in array index: ", pir_array.nonzero())

    # continue

    stats.process_frame(grid)
    midi.process_frame(stats, pir_array)
    graph.process_frame(grid, stats)
