#!/usr/bin/env bash
set -e

python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

python -m pip install -U pip

# Install editable + dev + notebook extras
python -m pip install -e ".[dev,notebook]"

# Register Jupyter kernel
python -m ipykernel install --user --name astrocalc --display-name "Python (astrocalc)"

# Strip notebook outputs on commit (repo-local git config)
python -m nbstripout --install --attributes .gitattributes --keep-output false

# Enable git hooks
python -m pre_commit install >/dev/null

echo "Done! Select kernel: Python (astrocalc)"
