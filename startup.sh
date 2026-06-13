#!/bin/bash
# Startup script for Azure App Service (Linux)
# This script activates the virtual environment and starts the FastAPI app

set -e

echo "Starting Inventory API..."

# Install dependencies if needed
if [ ! -d "venv3.0" ]; then
    echo "Creating virtual environment..."
    python -m venv venv3.0
fi

# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Start the application
echo "Starting Uvicorn server..."
python -m uvicorn main:app --host 0.0.0.0 --port 8000
