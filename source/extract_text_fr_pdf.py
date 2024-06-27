import fitz  # PyMuPDF
import re

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