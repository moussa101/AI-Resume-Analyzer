#!/usr/bin/env python3
"""Script to convert test data files to PDF and DOCX formats."""

import os
from pathlib import Path

# Check if required libraries are installed
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.units import inch
except ImportError:
    print("Installing reportlab...")
    os.system("pip install reportlab")
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.units import inch

try:
    from docx import Document
    from docx.shared import Pt, Inches
except ImportError:
    print("Installing python-docx...")
    os.system("pip install python-docx")
    from docx import Document
    from docx.shared import Pt, Inches


def txt_to_pdf(txt_path: str, pdf_path: str):
    """Convert a text file to PDF."""
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=6
    )
    
    story = []
    for line in content.split('\n'):
        if line.strip():
            # Escape special characters for reportlab
            line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(line, normal_style))
        else:
            story.append(Spacer(1, 12))
    
    doc.build(story)
    print(f"Created: {pdf_path}")


def txt_to_docx(txt_path: str, docx_path: str):
    """Convert a text file to DOCX."""
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    doc = Document()
    
    for line in content.split('\n'):
        para = doc.add_paragraph(line)
        para.style.font.size = Pt(11)
    
    doc.save(docx_path)
    print(f"Created: {docx_path}")


def main():
    base_dir = Path(__file__).parent
    
    # Process resumes
    resumes_dir = base_dir / "resumes"
    for txt_file in resumes_dir.glob("*.txt"):
        pdf_path = txt_file.with_suffix('.pdf')
        docx_path = txt_file.with_suffix('.docx')
        
        txt_to_pdf(str(txt_file), str(pdf_path))
        txt_to_docx(str(txt_file), str(docx_path))
    
    # Process job descriptions
    jd_dir = base_dir / "job_descriptions"
    for txt_file in jd_dir.glob("*.txt"):
        pdf_path = txt_file.with_suffix('.pdf')
        docx_path = txt_file.with_suffix('.docx')
        
        txt_to_pdf(str(txt_file), str(pdf_path))
        txt_to_docx(str(txt_file), str(docx_path))
    
    print("\nAll files converted successfully!")


if __name__ == "__main__":
    main()
