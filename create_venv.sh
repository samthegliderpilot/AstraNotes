#!/usr/bin/env bash
set -e

python3 -m venv .venv
source .venv/bin/activate

python -m pip install -U pip
pip install -e .

python -m ipykernel install --user --name astrocalc --display-name "Python (astrocalc)"

echo "Done! Select kernel: Python (astrocalc)"