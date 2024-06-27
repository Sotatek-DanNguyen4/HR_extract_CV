import docx2txt
# Hàm để trích xuất văn bản từ file DOCX
def extract_text_from_docx(docx_path):
    return docx2txt.process(docx_path)