#!/bin/bash
# Build script for Render (optional; Render can use Build Command instead)
# In Render dashboard, set Build Command to:
#   ./build.sh
# so the vector index is built at deploy time. Start Command stays: uvicorn main:app --host 0.0.0.0 --port $PORT
set -euo pipefail

echo "Installing Python dependencies..."
pip install -r requirements.txt

MAX_PAPERS="${MAX_PAPERS:-5000}"
echo "Building dataset and index (MAX_PAPERS=${MAX_PAPERS})..."
python initialize_dataset.py --max-papers "${MAX_PAPERS}"

echo "Build completed successfully!"
