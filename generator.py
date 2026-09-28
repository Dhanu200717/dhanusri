import os
import io
import re
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from fpdf import FPDF
from config import LOGO_PATH


def sanitize_text(text: str) -> str:
    """
    Removes special characters and typographic quotes to ensure clean formatting.
    Converts smart quotes, dashes, bullets, and non-ASCII characters to standard counterparts.
    """
    if not text:
        return ""
    
    replacements = {
        "\u2018": "'",   # Left single quote
        "\u2019": "'",   # Right single quote
        "\u201c": '"',   # Left double quote
        "\u201d": '"',   # Right double quote
        "\u2014": " - ", # Em dash
        "\u2013": " - ", # En dash
        "\u2026": "...", # Ellipsis
        "\u2022": "* ",  # Bullet symbol
        "\u00a0": " ",   # Non-breaking space
        "\u200b": "",    # Zero-width space
        "\ufeff": "",    # BOM
        "\u2122": "(TM)",
        "\u00ae": "(R)",
        "\u00a9": "(C)",
    }
    
    sanitized = text
    for orig, rep in replacements.items():
        sanitized = sanitized.replace(orig, rep)
    
    # Strip any residual non-latin-1 characters that would crash standard FPDF
    cleaned_chars = []
    for ch in sanitized:
        if ord(ch) < 256:
            cleaned_chars.append(ch)
        else:
            cleaned_chars.append(" ")
    
    return "".join(cleaned_chars)


class LegalEasePDF(FPDF):
    """
    Custom FPDF class with LegalEase branding:
    - Header with logo on pages
    - Footer on all pages: LegalEase Inc. | contact@legalease.com | All Rights Reserved.
    """
    def __init__(self, doc_type: str, logo_path: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.doc_type = doc_type
        self.logo_path = logo_path
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        # Header with center-aligned Logo if available
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                # Center logo (page width 210mm, logo width ~35mm)
                self.image(self.logo_path, x=87, y=10, w=36)
                self.set_y(28)
            except Exception:
                self.set_y(20)
        else:
            self.set_y(15)
            self.set_font("Helvetica", "B", 14)
            self.set_x(self.l_margin)
            self.cell(self.epw, 10, "LegalEase", align="C")
            self.ln(8)

        if self.page_no() == 1 and self.doc_type:
            self.set_font("Helvetica", "B", 15)
            self.set_x(self.l_margin)
            self.cell(self.epw, 8, sanitize_text(self.doc_type), align="C")
            self.ln(10)
        
        self.set_x(self.l_margin)

    def footer(self):
        # Position footer at 15 mm from bottom
        self.set_y(-18)
        self.set_draw_color(200, 200, 200)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.set_y(-14)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(100, 100, 100)
        self.set_x(self.l_margin)
        footer_text = "LegalEase Inc. | contact@legalease.com | All Rights Reserved."
        self.cell(self.epw, 8, f"{footer_text}   (Page {self.page_no()})", align="C")


def format_pdf(text: str, doc_type: str) -> bytes:
    """
    Generates a professionally formatted PDF using FPDF with:
    - Center-aligned logo header
    - Formatted bold headings
    - Bullet-style terms & clauses
    - Footer on all pages
    """
    clean_text = sanitize_text(text)
    clean_doc_type = sanitize_text(doc_type or "Legal Document")

    logo_file = str(LOGO_PATH) if LOGO_PATH.exists() else None
    pdf = LegalEasePDF(doc_type=clean_doc_type, logo_path=logo_file)
    pdf.set_margins(18, 20, 18)
    pdf.add_page()
    pdf.set_x(pdf.l_margin)
    
    # Body text styling
    pdf.set_text_color(30, 30, 30)

    lines = clean_text.splitlines()
    for line in lines:
        line_str = line.strip()
        pdf.set_x(pdf.l_margin)
        if not line_str:
            pdf.ln(3)
            continue
        
        # Check for headings (markdown #, ##, ### or numbered headings like 1. Title)
        if line_str.startswith("#"):
            heading_text = line_str.lstrip("#").strip()
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(20, 35, 60)
            pdf.ln(3)
            pdf.multi_cell(pdf.epw, 6, heading_text)
            pdf.ln(2)
            pdf.set_text_color(30, 30, 30)
        elif re.match(r"^\d+[\.\)]\s+", line_str):
            pdf.set_font("Helvetica", "B", 11)
            pdf.ln(2)
            pdf.multi_cell(pdf.epw, 6, line_str)
            pdf.set_font("Helvetica", "", 10)
        elif line_str.startswith("- ") or line_str.startswith("* "):
            pdf.set_font("Helvetica", "", 10)
            bullet_text = "  o " + line_str[2:].strip()
            pdf.multi_cell(pdf.epw, 5, bullet_text)
        elif line_str.upper() == line_str and len(line_str) > 3 and not line_str.startswith("{"):
            # Capitalized legal section titles (e.g. WITNESSETH:, NOW, THEREFORE,)
            pdf.set_font("Helvetica", "B", 10)
            pdf.ln(2)
            pdf.multi_cell(pdf.epw, 5, line_str)
            pdf.set_font("Helvetica", "", 10)
        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(pdf.epw, 5, line_str)

    # Return PDF bytes
    output_buffer = io.BytesIO()
    pdf_output = pdf.output()
    if isinstance(pdf_output, str):
        output_buffer.write(pdf_output.encode("latin-1"))
    elif isinstance(pdf_output, bytearray):
        output_buffer.write(bytes(pdf_output))
    else:
        output_buffer.write(pdf_output)
    
    return output_buffer.getvalue()


def format_docx(text: str, doc_type: str) -> bytes:
    """
    Generates a structured .docx file using python-docx with:
    - Embedded logo on front page
    - Times New Roman font (12pt body, bold headings)
    - Auto-generated terms table for terms/clauses
    - Footer in the document
    """
    clean_text = sanitize_text(text)
    clean_doc_type = sanitize_text(doc_type or "Legal Document")

    doc = Document()

    # Set margins
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Base style font: Times New Roman
    style = doc.styles["Normal"]
    font = style.font
    font.name = "Times New Roman"
    font.size = Pt(11)
    font.color.rgb = RGBColor(30, 30, 30)

    # Add Logo if present
    if LOGO_PATH.exists():
        try:
            logo_p = doc.add_paragraph()
            logo_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            logo_run = logo_p.add_run()
            logo_run.add_picture(str(LOGO_PATH), width=Inches(2.2))
        except Exception:
            pass

    # Document Title
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title_p.add_run(clean_doc_type.upper())
    title_run.font.name = "Times New Roman"
    title_run.font.size = Pt(16)
    title_run.bold = True
    title_run.font.color.rgb = RGBColor(20, 35, 60)
    title_p.paragraph_format.space_after = Pt(16)

    # Process lines
    lines = clean_text.splitlines()
    in_terms_section = False
    terms_list = []

    def flush_terms_table():
        nonlocal terms_list
        if not terms_list:
            return
        table = doc.add_table(rows=1, cols=2)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False

        # Header Row
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = "#"
        hdr_cells[1].text = "Clause / Term Description"
        
        # Style header row
        for i, cell in enumerate(hdr_cells):
            shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="1E293B"/>')
            cell._tc.get_or_add_tcPr().append(shading)
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.name = "Times New Roman"
                    run.font.size = Pt(10)
                    run.bold = True
                    run.font.color.rgb = RGBColor(255, 255, 255)

        for idx, term in enumerate(terms_list, 1):
            row_cells = table.add_row().cells
            row_cells[0].text = str(idx)
            row_cells[1].text = term
            for cell in row_cells:
                shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{"F8FAFC" if idx % 2 == 1 else "FFFFFF"}"/>')
                cell._tc.get_or_add_tcPr().append(shading)
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.name = "Times New Roman"
                        run.font.size = Pt(10)

        # Set column widths
        for row in table.rows:
            row.cells[0].width = Inches(0.6)
            row.cells[1].width = Inches(5.9)
            
        doc.add_paragraph() # Spacing after table
        terms_list = []

    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue

        # Check for headings
        if line_str.startswith("#"):
            flush_terms_table()
            in_terms_section = False
            heading_level = min(line_str.count("#"), 3)
            heading_content = line_str.lstrip("#").strip()
            
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run(heading_content)
            run.font.name = "Times New Roman"
            run.font.size = Pt(14 if heading_level == 1 else (12 if heading_level == 2 else 11))
            run.bold = True
            run.font.color.rgb = RGBColor(20, 35, 60)

            if "term" in heading_content.lower() or "condition" in heading_content.lower():
                in_terms_section = True

        elif in_terms_section and (line_str.startswith("- ") or line_str.startswith("* ") or ";" in line_str):
            term_clean = line_str.lstrip("- *").strip().rstrip(";")
            if term_clean:
                terms_list.append(term_clean)

        elif re.match(r"^\d+[\.\)]\s+", line_str):
            flush_terms_table()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(line_str)
            run.font.name = "Times New Roman"
            run.font.size = Pt(11)
            run.bold = True
            run.font.color.rgb = RGBColor(20, 35, 60)

        elif line_str.startswith("- ") or line_str.startswith("* "):
            p = doc.add_paragraph(style='List Bullet')
            run = p.add_run(line_str.lstrip("- *").strip())
            run.font.name = "Times New Roman"
            run.font.size = Pt(11)

        else:
            flush_terms_table()
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.15
            run = p.add_run(line_str)
            run.font.name = "Times New Roman"
            run.font.size = Pt(11)
            if line_str.isupper() and len(line_str) > 3:
                run.bold = True

    flush_terms_table()

    # Add Footer
    for section in doc.sections:
        footer = section.footer
        footer_p = footer.paragraphs[0]
        footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        footer_run = footer_p.add_run("LegalEase Inc. | contact@legalease.com | All Rights Reserved.")
        footer_run.font.name = "Times New Roman"
        footer_run.font.size = Pt(9)
        footer_run.font.italic = True
        footer_run.font.color.rgb = RGBColor(128, 128, 128)

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


def format_html_preview(text: str) -> str:
    """
    Converts AI-generated markdown/text output to stylized HTML blocks
    for an elegant dark-themed scrollable card preview in Streamlit.
    """
    clean_text = sanitize_text(text)
    html_lines = []

    for raw_line in clean_text.splitlines():
        line = raw_line.strip()
        if not line:
            html_lines.append("<div style='height: 10px;'></div>")
            continue

        # Markdown Headings
        if line.startswith("### "):
            html_lines.append(f"<h4 style='color: #60a5fa; margin-top: 14px; margin-bottom: 6px; font-weight: 600;'>{line[4:]}</h4>")
        elif line.startswith("## "):
            html_lines.append(f"<h3 style='color: #93c5fd; margin-top: 18px; margin-bottom: 8px; border-bottom: 1px solid #334155; padding-bottom: 4px; font-weight: 700;'>{line[3:]}</h3>")
        elif line.startswith("# "):
            html_lines.append(f"<h2 style='color: #38bdf8; margin-top: 22px; margin-bottom: 10px; text-align: center; font-weight: 800;'>{line[2:]}</h2>")
        elif re.match(r"^\d+[\.\)]\s+", line):
            html_lines.append(f"<p style='color: #f1f5f9; font-weight: 600; margin-top: 10px; margin-bottom: 4px;'>{line}</p>")
        elif line.startswith("- ") or line.startswith("* "):
            bullet_body = line[2:].strip()
            # replace bold markdown **text** with <strong>text</strong>
            bullet_body = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", bullet_body)
            html_lines.append(f"<li style='color: #cbd5e1; margin-left: 20px; line-height: 1.6;'>{bullet_body}</li>")
        else:
            formatted_line = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", line)
            if formatted_line.isupper() and len(formatted_line) > 3:
                html_lines.append(f"<p style='color: #94a3b8; font-weight: bold; letter-spacing: 0.5px; margin-top: 12px; margin-bottom: 4px;'>{formatted_line}</p>")
            else:
                html_lines.append(f"<p style='color: #e2e8f0; line-height: 1.7; margin-bottom: 8px;'>{formatted_line}</p>")

    inner_html = "\n".join(html_lines)
    return f"""
    <div style='
        background-color: #0f172a;
        color: #e2e8f0;
        padding: 24px 30px;
        border-radius: 12px;
        border: 1px solid #1e293b;
        box-shadow: 0 4px 14px rgba(0,0,0,0.4);
        max-height: 520px;
        overflow-y: auto;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        font-size: 14.5px;
    '>
        {inner_html}
    </div>
    """
