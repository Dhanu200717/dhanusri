# System Architecture - LegalEase

## Component Interaction Flow

```
[ User Input (Streamlit) ]
           │
           ▼
[ FastAPI Backend (POST /generate) ]
           │
           ▼
[ ai_core.gemini_generator (Google Gemini 1.5 Pro) ]
           │
           ▼
[ Structured Legal Document Text ]
           │
           ├──► [ HTML Preview (Streamlit Dark Theme) ]
           ├──► [ Inline Text Editor (Streamlit) ]
           └──► [ Formatting Engine (ai_core.generator) ]
                     │
                     ├──► [.TXT File Export]
                     ├──► [.DOCX Word Document (Tables, Logo, Times New Roman)]
                     └──► [.PDF Branded Document (Header Logo, Footers)]
```

## Module Responsibilities

1. **`frontend/app.py`**:
   - Manages user input forms (document type, stakeholders, clauses, dates).
   - Coordinates API requests to the backend server.
   - Manages state for inline text editing and dynamic download buttons.

2. **`legalEaseAPI/main.py` & `routes.py`**:
   - Exposes RESTful endpoints.
   - Validates incoming request payloads with Pydantic (`DocumentRequest`).
   - Delegates prompt generation to `GeminiDocumentGenerator`.

3. **`ai_core/gemini_generator.py`**:
   - Integrates Google Generative AI SDK (`gemini-1.5-pro`).
   - Crafts contextual legal prompts ensuring clause divisions, recitals, and standard legal structure.

4. **`ai_core/generator.py`**:
   - `sanitize_text`: Cleans special typographic quotes and unicode entities.
   - `format_docx`: Generates Word documents containing headers, tables for clauses, and footers.
   - `format_pdf`: Generates PDF documents with FPDF, adding company logo and running footers.
   - `format_html_preview`: Stylizes document for live interactive preview.
