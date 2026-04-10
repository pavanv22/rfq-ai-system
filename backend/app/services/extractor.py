import pdfplumber
from docx import Document
import pytesseract
from PIL import Image
import os

def extract_text(file_path):
    if file_path.endswith(".pdf"):
        return extract_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_docx(file_path)
    elif file_path.endswith(".png") or file_path.endswith(".jpg"):
        return extract_image(file_path)
    else:
        return "Unsupported format"

def extract_pdf(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            text += f"\n[Page {i+1}]\n"
            text += page.extract_text() or ""
    return text

def extract_docx(path):
    doc = Document(path)
    return "\n".join([p.text for p in doc.paragraphs])

def extract_image(path):
    img = Image.open(path)
    return pytesseract.image_to_string(img)