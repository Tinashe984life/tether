Write-Host "Setting up backend virtualenv and installing Python deps..."
python -m venv backend\venv
.\backend\venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
Write-Host "Frontend scaffold must be created locally using npm/yarn. See frontend/README.md."
