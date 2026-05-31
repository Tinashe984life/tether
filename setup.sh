#!/usr/bin/env bash
set -e

echo "Setting up backend virtualenv and installing Python deps..."
python -m venv backend/venv
source backend/venv/bin/activate
pip install -r backend/requirements.txt

echo "Frontend scaffold must be created locally using npm/yarn. See frontend/README.md."
