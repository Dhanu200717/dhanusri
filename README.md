# LegalEase: AI-Powered Legal Document Generator

**LegalEase** is an AI-powered legal document generation platform built with **FastAPI**, **Google Gemini AI**, and **Streamlit**. It automates the drafting of standard and custom legal contracts, NDAs, employment agreements, and lease terms with live previews, inline editing, and multi-format exports (.PDF, .DOCX, .TXT).

---

## 📁 Project Architecture

```
LEGALEASE/
├── ai_core/
│   ├── __init__.py
│   ├── gemini_generator.py      # Google Gemini 1.5 Pro integration
│   └── generator.py             # DOCX, PDF, HTML formatters & text sanitization
├── docs/
│   ├── ARCHITECTURE.md          # Architectural breakdown
│   └── SETUP.md                 # Setup and deployment guidelines
├── frontend/
│   └── app.py                   # Streamlit interactive UI
├── Image/
│   ├── inverseLogo.png          # Light logo for dark mode UI
│   └── Logo.png                 # Dark logo for Word/PDF document branding
├── legalEaseAPI/
│   ├── __init__.py
│   ├── main.py                  # FastAPI server entry point
│   └── routes.py                # Generation endpoint (/generate)
├── venv/                        # Python virtual environment
├── .env                         # API keys and environment variables
├── config.py                    # Global configuration
├── requirements.txt             # Project dependencies
├── run.sh                       # Linux / Mac launcher script
├── run.bat                      # Windows launcher script
└── README.md
```

---

## 🚀 Quick Start Guide

### 1. Configure Your Gemini API Key
Open `.env` and insert your Google Gemini API key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-pro
BACKEND_URL=http://localhost:8000
```

### 2. Run the Application

#### Option A: Windows (One Click)
Double-click `run.bat` or run:
```powershell
.\run.bat
```

#### Option B: Manual Launch (Two Terminals)

**Terminal 1 - FastAPI Backend:**
```powershell
.\venv\Scripts\activate
uvicorn legalEaseAPI.main:app --reload --host 0.0.0.0 --port 8000
```
- API Docs: `http://localhost:8000/docs`
- Healthcheck: `http://localhost:8000/`

**Terminal 2 - Streamlit Frontend:**
```powershell
.\venv\Scripts\activate
streamlit run frontend/app.py
```
- Web Application: `http://localhost:8501`

---

## 🛠️ Features

1. **AI Legal Document Generation**: High-precision legal drafting using `gemini-1.5-pro` with dynamic prompt building based on document type, parties, terms, and effective dates.
2. **Interactive UI**: Clean, responsive layout with embedded branding and status monitors.
3. **HTML Dark Mode Preview**: Live semantic rendering of generated legal contracts.
4. **Inline Editing**: Allows users to customize clauses and tweak wording before exporting.
5. **Multi-Format Exports**:
   - **.TXT**: Clean plain text representation.
   - **.DOCX**: Microsoft Word document formatted in Times New Roman, with embedded company logo, terms table, and legal footer.
   - **.PDF**: Branded PDF generated via FPDF with centered logo, section headings, bulleted clauses, and per-page footer.
