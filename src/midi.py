from collections import deque
import os
import random
import time
import mido
import numpy as np

from src.stats import StatsController

# Smoothing constraig
WINDOW_SIZE = 10  # Number of samples to consider for moving average
HYSTERESIS = 0.05  # Minimum change required to update MIDI value
SMOOTHING_FACTOR = 0.2  # Exponential smoothing factor (0 to 1)


weighted_x_history = deque(maxlen=WINDOW_SIZE)
smoothed_value = 0
last_midi_value = 0


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


def mapFromTo(x, a, b, c, d):
    y = (x - a) / (b - a) * (d - c) + c
    return max(c, min(d, y))


class MidiController:
    def __init__(self):

        on_windows = os.name == "nt"

        if on_windows:
            output_names = mido.get_output_names()
            print("Output names:", output_names)
            self.midi_out = mido.open_output(output_names[1])
        else:
            mido.set_backend("mido.backends.portmidi")
            # os.set_blocking(p.stdout.fileno(), False)  # That's what you are looking for
            output_names = mido.get_output_names()
            print("Output names:", output_names)
            self.midi_out = mido.open_output(output_names[-1])

    def send(self, msg: mido.Message):
        self.midi_out.send(msg)

    def process_frame(self, stats_ctlr: StatsController, pir_array: np.array):
        n_x = stats_ctlr.stats_data["Weighted X"][-1]
        n_y = stats_ctlr.stats_data["Weighted Y"][-1]
        # midi_x_value = get_smooth_midi_value(n_x)
        midi_x_value = int(mapFromTo(n_y, 0, 8, 0, 127))
        # human_detected = mapFromTo(stats_ctlr.max_temp, 7.0, 9.0, 0, 1)
        human_detected = mapFromTo(stats_ctlr.max_temp, 15, 20, 0, 1)

        self.send(
            mido.Message(
                "control_change",
                control=1,
                value=midi_x_value,
            )
        )

        self.send(
            mido.Message(
                "control_change",
                control=2,
                value=int(human_detected * 127),
            )
        )

        note_mappings = {1: 60, 2: 72}

        for i, pir in enumerate(pir_array):
            if i in [0]:
                continue

            note_value = note_mappings.get(i, 60)

            self.send(
                mido.Message(
                    "note_on" if pir else "note_off",
                    note=note_value,
                    # velocity=64,
                )
            )

        # if random.random() < 0.1:  # 10% chance to send trigger
        #     note = 60  # MIDI note number for C3
        #     velocity = random.randint(64, 127)  # Random velocity between 64 and 127

        #     self.send(mido.Message("note_on", note=note, velocity=velocity))
        #     print(f"Note On: C3 (note {note}) with velocity {velocity}")

        #     time.sleep(0.05)  # Hold the note for 100ms

        #     self.send(mido.Message("note_off", note=note))
        #     print(f"Note Off: C3 (note {note})")

        print("Raw Weighted X:", n_x)
        print("Smoothed MIDI value:", midi_x_value)
        print(f"Human {human_detected}")
