set -e
cd "$(dirname "$0")"

brew install pipx
pipx install poetry
brew install portmidi
poetry install