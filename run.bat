@echo off
title LegalEase Launcher
echo ========================================================
echo Starting LegalEase: AI-Powered Legal Document Generator
echo ========================================================

call venv\Scripts\activate.bat

echo Starting FastAPI Backend on http://localhost:8000 ...
start "LegalEase Backend" cmd /k "venv\Scripts\uvicorn.exe legalEaseAPI.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo Starting Streamlit Frontend on http://localhost:8501 ...
venv\Scripts\streamlit.exe run frontend\app.py

pause
