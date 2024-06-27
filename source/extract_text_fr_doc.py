import os
import re
import subprocess
from source.extract_text_fr_docx import extract_text_from_docx
# Hàm để chuyển đổi file DOC sang DOCX sử dụng LibreOffice
def convert_doc_to_docx(doc_path):
    output_dir = os.path.dirname(doc_path)
    subprocess.run(['soffice', '--headless', '--convert-to', 'docx', '--outdir', output_dir, doc_path])
    base = os.path.splitext(doc_path)[0]
    output_path = base + '.docx'
    return output_path

# Hàm để trích xuất văn bản từ file DOC bằng cách chuyển đổi sang DOCX
def extract_text_from_doc(doc_path):
    docx_path = convert_doc_to_docx(doc_path)
    text = extract_text_from_docx(docx_path)
    os.remove(docx_path)  # Xóa file docx tạm thời
    return text