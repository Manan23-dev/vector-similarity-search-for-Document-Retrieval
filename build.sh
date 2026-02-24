#!/bin/bash
# Build script for Render (optional; Render can use Build Command instead)
# In Render dashboard, set Build Command to:
#   pip install -r requirements.txt && python initialize_dataset.py --max-papers 5000
# so the vector index is built at deploy time. Start Command stays: uvicorn main:app --host 0.0.0.0 --port $PORT
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Build completed successfully!"
