import os
import mido


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
            self.midi_out = mido.open_output(output_names[1])

    def send(self, msg: mido.Message):
        self.midi_out.send(msg)
