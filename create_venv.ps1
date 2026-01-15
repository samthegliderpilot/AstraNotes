python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install -U pip
pip install -e .

python -m ipykernel install --user --name astrocalc --display-name "Python (astrocalc)"
nbstripout --install --attributes .gitattributes --keep-output false
python -m pre_commit install | Out-Null
Write-Host "Done! Select kernel: Python (astrocalc)" -ForegroundColor Green
