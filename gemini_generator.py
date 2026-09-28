import os
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import google.generativeai as genai
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

class GeminiDocumentGenerator:
    def __init__(self, model_name: str = None):
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-3-flash")
        
        if self.api_key and self.api_key != "your_gemini_api_key_here":
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        else:
            self.model = None

    def _ensure_model(self):
        """Re-check and configure API key dynamically if it was updated."""
        if not self.model:
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if not api_key or api_key == "your_gemini_api_key_here":
                raise ValueError(
                    "GEMINI_API_KEY is not set or invalid. "
                    "Please set your Gemini API key in the .env file."
                )
            self.api_key = api_key
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)

    def generate_document(self, document_type: str, parties: str, terms: str, dates: str) -> str:
        """
        Generate a structured legal document using Google Gemini AI.
        """
        self._ensure_model()

        prompt = (
            f"Generate a comprehensive legal document titled '{document_type}'\n"
            f"Involved parties: {parties}\n"
            f"Effective Date: {dates}\n"
            f"Terms and conditions: {terms}\n"
            f"Ensure formal legal structure with multiple sections and legal clauses."
        )

        candidate_models = [
            "gemini-3.8-flash",
        ]
        
        last_error = None
        for m_name in dict.fromkeys(candidate_models): # unique while preserving order
            try:
                gen_model = genai.GenerativeModel(m_name)
                response = gen_model.generate_content(prompt)
                if hasattr(response, "text") and response.text:
                    return response.text
            except Exception as e:
                last_error = e
                # Continue trying next candidate if 404 or unsupported
                if "not found" in str(e).lower() or "404" in str(e) or "not supported" in str(e).lower():
                    continue
                else:
                    raise RuntimeError(f"Error generating legal document via Gemini API: {str(e)}")
                    
        raise RuntimeError(f"Error generating legal document via Gemini API: {str(last_error)}")

