# Usage

## Setup

- Run .`/setup_macos.sh`
- Using Audio MIDI Setup App (Enable the IAC Driver):
  - Go to Window > Show MIDI Studio
  - Double click on the IAC Driver
  - Check the "Device is online" checkbox

### Windows

- Install loopMidi https://www.tobias-erichsen.de/software/loopmidi.html
- Make a loopback port

#### ssh on windows

` type $env:USERPROFILE\.ssh\id_rsa.pub | ssh "edeetee@raspberrypi.local" "cat >> .ssh/authorized_keys"`

## Running

- Make sure the RPI is connected to the same network as the host machine
- Ensure you can connect to the RPI using ssh
- Run .`/run_macos.sh`
