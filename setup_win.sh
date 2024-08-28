set -e
cd "$(dirname "$0")"

python -m pip install --user pipx
pipx install poetry
wsl --install
poetry install