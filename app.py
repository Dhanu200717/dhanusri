import os
import sys
from pathlib import Path

# Self-bootstrap if run directly via standard Python (e.g. VS Code Play button)
try:
    from streamlit.runtime.scriptrunner import get_script_run_ctx
    if get_script_run_ctx() is None:
        import streamlit.web.cli as stcli
        sys.argv = ["streamlit", "run", str(Path(__file__).resolve()), "--server.port", "8501"]
        sys.exit(stcli.main())
except Exception:
    pass

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st
import requests
from config import BACKEND_URL, INVERSE_LOGO_PATH, LOGO_PATH
from ai_core.generator import sanitize_text, format_docx, format_pdf, format_html_preview

# Streamlit Page Configuration
st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="centered"
)

# Custom CSS for polished layout matching the document design
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        margin-top: -10px;
        margin-bottom: 25px;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1rem;
    }
    .stDownloadButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# Logo Display
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    # Use inverseLogo if available, fallback to Logo
    logo_to_display = INVERSE_LOGO_PATH if INVERSE_LOGO_PATH.exists() else LOGO_PATH
    if logo_to_display.exists():
        st.image(str(logo_to_display), use_container_width=True)

# Header and Title
st.markdown(
    "<h2 class='main-title'>AI Legal Document Generator</h2>",
    unsafe_allow_html=True
)

# Sidebar with Information & API status
with st.sidebar:
    st.header("⚖️ About LegalEase")
    st.markdown(
        """
        **LegalEase** generates customized, professional legal agreements, NDAs, contracts, and employment letters powered by Google's Gemini AI.
        
        **Supported Formats:**
        - Plain Text (`.txt`)
        - Microsoft Word (`.docx`)
        - Branded PDF (`.pdf`)
        """
    )
    
    st.markdown("---")
    st.subheader("⚙️ System Status")
    
    # Quick health check of FastAPI backend
    backend_status = "🔴 Offline"
    try:
        r = requests.get(f"{BACKEND_URL}/", timeout=2)
        if r.status_code == 200:
            backend_status = "🟢 Online"
    except Exception:
        backend_status = "🔴 Offline"
    
    st.write(f"**Backend API:** {backend_status}")
    st.caption(f"API Target: `{BACKEND_URL}`")

    # API Key helper in sidebar if needed
    env_key = os.getenv("GEMINI_API_KEY", "")
    if not env_key or env_key == "your_gemini_api_key_here":
        st.warning("⚠️ GEMINI_API_KEY is not configured in `.env`.")

# User Input Interface
st.markdown("### Document Details")

document_type = st.text_input(
    "Document Type (Ex. Agreement, Contract, NDA)",
    placeholder="Freelance Work Contract",
    help="Enter the specific type of document you need."
)

parties = st.text_area(
    "Parties Involved",
    placeholder="Jane Doe (Service Provider), TechNova Inc. (Client)",
    help="Enter names and official roles of all participating parties."
)

terms = st.text_area(
    "Terms & Conditions (Use semicolons for bullet points)",
    placeholder="Work must be delivered by May 15, 2025;\nPayment will be made within 7 days of invoice;\nThe client retains intellectual property rights;\nConfidentiality must be maintained at all times",
    help="List specific requirements, clauses, payment terms, or covenants separated by semicolons."
)

dates = st.text_input(
    "Effective Date",
    placeholder="April 15, 2025",
    help="The starting or execution date of this legal agreement."
)

# Generate Document Button
if st.button("enerate Document", type="primary"):
    if not document_type.strip():
        st.error("Please specify the 'Document Type'.")
    elif not parties.strip():
        st.error("Please enter the 'Parties Involved'.")
    else:
        with st.spinner("Drafting your legal document with Gemini AI..."):
            try:
                payload = {
                    "document_type": document_type.strip(),
                    "parties": parties.strip(),
                    "terms": terms.strip(),
                    "dates": dates.strip() if dates.strip() else "As of execution date"
                }
                
                response = requests.post(f"{BACKEND_URL}/generate", json=payload, timeout=60)
                
                if response.status_code == 200:
                    raw_doc = response.json().get("document", "")
                    clean_doc = sanitize_text(raw_doc)
                    st.session_state["generated_text"] = clean_doc
                    st.session_state["document_type"] = document_type.strip()
                    st.session_state["show_edit"] = False
                    st.rerun()
                else:
                    err_msg = response.json().get("detail", response.text)
                    st.error(f"Error from LegalEase backend: {err_msg}")
            except requests.exceptions.ConnectionError:
                st.error(
                    f"Could not connect to FastAPI backend at {BACKEND_URL}. "
                    "Please ensure the backend is running via `python legalEaseAPI/main.py`."
                )
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")

st.caption("Click 'Generate Document' to start")

# Render Generated Document Section
if "generated_text" in st.session_state and st.session_state["generated_text"]:
    st.markdown("---")
    st.success("Document Generated Successfully!")
    
    current_doc = st.session_state["generated_text"]
    current_type = st.session_state.get("document_type", "Legal_Document")
    safe_file_name = current_type.replace(" ", "_").lower()

    # Step 2: HTML Preview Rendering
    st.markdown("#### Document Preview")
    preview_html = format_html_preview(current_doc)
    st.markdown(preview_html, unsafe_allow_html=True)

    # Step 3: Editable Document Preview Toggle
    st.write("")
    col_edit, _ = st.columns([1, 1])
    with col_edit:
        btn_label = "✖️ Close Editor" if st.session_state.get("show_edit") else "🖊️ Click to Edit Document"
        if st.button(btn_label):
            st.session_state["show_edit"] = not st.session_state.get("show_edit", False)
            st.rerun()

    if st.session_state.get("show_edit"):
        st.markdown("##### Edit Document Below:")
        edited_content = st.text_area(
            "Document Editor",
            value=current_doc,
            height=350,
            label_visibility="collapsed"
        )
        if edited_content != current_doc:
            st.session_state["generated_text"] = edited_content
            current_doc = edited_content
            st.caption("Changes saved in current session.")

    # Step 4: Multi-Format Download Options
    st.markdown("#### Download / Save Document")
    st.write("Save the document in any of the following formats:")

    col_txt, col_docx, col_pdf = st.columns(3)
    
    with col_txt:
        st.download_button(
            label="📄 Download as .TXT",
            data=current_doc,
            file_name=f"{safe_file_name}.txt",
            mime="text/plain"
        )

    with col_docx:
        docx_data = format_docx(current_doc, current_type)
        st.download_button(
            label="📄 Download as .DOCX",
            data=docx_data,
            file_name=f"{safe_file_name}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    with col_pdf:
        pdf_data = format_pdf(current_doc, current_type)
        st.download_button(
            label="📄 Download as .PDF",
            data=pdf_data,
            file_name=f"{safe_file_name}.pdf",
            mime="application/pdf"
        )
