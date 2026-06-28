import re
from fpdf import FPDF

class PDFReport(FPDF):
    def header(self):
        # Header banner styling
        self.set_fill_color(24, 28, 56) # Deep Navy blue
        self.rect(0, 0, 210, 30, 'F')
        
        self.set_text_color(255, 255, 255)
        self.set_font('helvetica', 'B', 16)
        self.cell(0, 10, 'DATASENTINEL AI - INCIDENT SUMMARY REPORT', align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(10)
        
    def footer(self):
        self.set_y(-15)
        self.set_text_color(128, 128, 128)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}} | Confidential - Enterprise Data Incident Commander', align='C')

def clean_text_for_pdf(text):
    """
    Cleans Unicode emojis and standardizes bullet points/characters
    to prevent encoding failures with standard PDF Helvetica fonts.
    """
    replacements = {
        "🚨": "[CRITICAL]",
        "📘": "[REPORT]",
        "⚙️": "[CONFIG]",
        "✅": "[RESOLVED]",
        "❌": "[FAILED]",
        "⚠️": "[WARNING]",
        "ℹ️": "[INFO]",
        "💡": "[TIP]",
        "—": "-",
        "–": "-",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    
    # Remove any other non-ASCII characters
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    return text

def generate_pdf_report(markdown_text):
    """
    Generates a PDF bytearray from markdown input by parsing header markers.
    """
    cleaned_markdown = clean_text_for_pdf(markdown_text)
    
    pdf = PDFReport()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    
    pdf.set_text_color(30, 30, 30)
    pdf.set_font("helvetica", size=10)
    
    lines = cleaned_markdown.split('\n')
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            pdf.ln(4)
            continue
            
        # Parse titles
        if stripped.startswith('# '):
            pdf.ln(6)
            pdf.set_font("helvetica", "B", 16)
            pdf.set_text_color(24, 28, 56)
            pdf.cell(0, 10, stripped[2:], new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("helvetica", "", 10)
            pdf.set_text_color(30, 30, 30)
            
        elif stripped.startswith('## '):
            pdf.ln(4)
            pdf.set_font("helvetica", "B", 13)
            pdf.set_text_color(40, 60, 120)
            pdf.cell(0, 8, stripped[3:], new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("helvetica", "", 10)
            pdf.set_text_color(30, 30, 30)
            
        elif stripped.startswith('### '):
            pdf.ln(3)
            pdf.set_font("helvetica", "B", 11)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(0, 6, stripped[4:], new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("helvetica", "", 10)
            pdf.set_text_color(30, 30, 30)
            
        elif stripped.startswith('*') or stripped.startswith('-'):
            pdf.set_font("helvetica", "", 10)
            # Remove markdown symbol
            content = stripped[1:].strip()
            # Indent bullet point
            pdf.cell(8)
            pdf.multi_cell(0, 5, f"o  {content}")
            
        else:
            # Inline bold parsing (basic)
            # Just print the line but handle multi-cell wrap
            pdf.set_font("helvetica", "", 10)
            pdf.multi_cell(0, 5, stripped)
            
    # output() in FPDF2 returns bytes directly if dest is not specified (or default is empty string)
    return bytes(pdf.output())
