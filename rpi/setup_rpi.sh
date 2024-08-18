# sudo apt-get install -y python3-pip python-scipy python-pygame i2c-tools
# sudo pip3 install colour adafruit-blinka numpy pygame scipy adafruit-circuitpython-amg88xx
set -e

sudo apt-get install -y pipx
pipx install poetry
pipx ensurepath

PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring ~/.local/bin/poetry install