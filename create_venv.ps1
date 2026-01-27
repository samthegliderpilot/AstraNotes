python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install -U pip

# Install editable + dev + notebook extras
python -m pip install -e ".[dev,notebook]"

# Register Jupyter kernel (idempotent-ish: re-running updates the spec)
python -m ipykernel install --user --name astranotes --display-name "Python (astranotes)"

# Strip notebook outputs on commit (repo-local git config)
python -m nbstripout --install --attributes .gitattributes --keep-output false

# Enable git hooks (pre-commit)
python -m pre_commit install | Out-Null

Write-Host "Done! Select kernel: Python (astranotes)" -ForegroundColor Green
