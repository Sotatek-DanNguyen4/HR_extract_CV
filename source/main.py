import os
from extract_text_fr_docx import extract_text_from_docx
from extract_text_fr_pdf import extract_text_from_pdf ,extract_text_from_pdf_2
from extract_text_fr_xlsx import extract_text_from_xlsx
from extract_field import extract_field
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from openpyxl import load_workbook
import tempfile
from typing import List
import os
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
os.environ["GROQ_API_KEY"] = "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"
app = FastAPI()

# # Hàm để kiểm tra loại file
# def check_file_type(file_path):
#     _, file_extension = os.path.splitext(file_path)
#     return file_extension.lower()

# # Đường dẫn đến file
# file_path = "/content/PM_Lê Thị Thu Phương.docx"  # Lấy tên file đã tải lên

# # Kiểm tra loại file
# file_type = check_file_type(file_path)

# # Trích xuất văn bản dựa trên loại file
# if file_type == ".pdf":
#     full_text = extract_text_from_pdf(file_path)  # Cần cài đặt và thêm hàm extract_text_from_pdf
# elif file_type == ".docx":
#     full_text = extract_text_from_docx(file_path)
# # elif file_type == ".doc":
# #     full_text = extract_text_from_doc(file_path)
# elif file_type == ".xlsx":
#     full_text = extract_text_from_xlsx(file_path)
# else:
#     raise ValueError("File không phải là PDF, DOCX hoặc XLSX.")
def read_file(file_path, file_ext):
    if file_ext == '.pdf':
        return extract_text_from_pdf(file_path) + " " + extract_text_from_pdf_2(file_path)
    elif file_ext == '.docx':
        return extract_text_from_docx(file_path)
    elif file_ext == '.xlsx':
        return extract_text_from_xlsx(file_path)
    else:
        return f"Unsupported file type: {file_ext}"
@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Lưu file vào thư mục cụ thể trên máy tính
        file_path = os.path.join("uploads", file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())
        # text="oke"
        file_name, file_ext = os.path.splitext(file.filename)
        text = read_file(file_path, file_ext.lower())

        # Xóa file sau khi đã xử lý xong (nếu cần thiết)
        os.remove(file_path)
        logger.info(f'filename: {file.filename}')
        logger.info("##############################################################")
        logger.info(f'text: {text}')
        logger.info("##############################################################")
        extracted_text = extract_field(text)
        logger.info(f'extracted: {extracted_text}')
        logger.info("##############################################################")
        return { 'filename': file.filename, 'text': extract_field(text) }
    except Exception as e:
        return { 'filename': file.filename, 'error': f"Failed to process file: {str(e)}" }
