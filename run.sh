#!/bin/bash
# LegalEase Startup Script

echo "Starting LegalEase FastAPI Backend..."
python -m uvicorn legalEaseAPI.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "Waiting for Backend to initialize..."
sleep 3

echo "Starting LegalEase Streamlit Frontend..."
streamlit run frontend/app.py

kill $BACKEND_PID
