# Setup & Verification Guide - LegalEase

## Prerequisites
- Python 3.10+
- Google Gemini API Key

## Setup Steps

1. **Activate Virtual Environment**:
   ```powershell
   .\venv\Scripts\activate
   ```

2. **Verify Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

3. **Configure API Key**:
   In `.env`:
   ```env
   GEMINI_API_KEY=AIzaSy...
   GEMINI_MODEL=gemini-1.5-pro
   BACKEND_URL=http://localhost:8000
   ```

4. **Start Backend**:
   ```powershell
   uvicorn legalEaseAPI.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Start Frontend**:
   ```powershell
   streamlit run frontend/app.py
   ```
