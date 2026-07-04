#!/bin/bash

# Exit immediately if any command fails
set -e

echo "=================================================="
echo "🚀 Launching Greenwood Admission ERP Assistant RAG"
echo "=================================================="

# Ensure SQLite DB is initialized
echo "Checking and seeding database schema..."
python -c "from database.sqlite_db import SchoolERPDatabase; SchoolERPDatabase()"

# Start FastAPI Backend in the background
echo "Starting FastAPI Backend Server on port 8000..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to boot up
echo "Waiting for FastAPI to become healthy..."
until curl -s http://localhost:8000/api/v1/health | grep -q "healthy"; do
  sleep 1
done
echo "FastAPI Backend is healthy and connected to SQL."

# Start Streamlit Frontend
echo "Starting Streamlit Frontend on port 8501..."
streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0

# Keep script running
wait $BACKEND_PID
