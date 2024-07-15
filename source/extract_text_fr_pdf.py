import fitz  # PyMuPDF
import re
import pdfplumber

def extract_text_from_pdf(pdf_path):
    # Mở file PDF
    pdf_document = fitz.open(pdf_path)
    # Trích xuất văn bản từ tất cả các trang của PDF
    full_text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        full_text += page.get_text()
    pdf_document.close()
    return full_text

def extract_text_from_pdf_2(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text