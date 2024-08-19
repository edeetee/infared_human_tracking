set -e
cd "$(dirname "$0")"

brew install pipx
pix install poetry
brew install portmidi
poetry install