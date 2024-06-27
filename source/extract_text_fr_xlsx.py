import openpyxl

def extract_text_from_xlsx(file_path):
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.worksheets[0]  # Chọn sheet đầu tiên

    data = []
    for row in sheet.iter_rows(values_only=True):
        # Lọc bỏ các ô có giá trị là None
        filtered_row = [cell for cell in row if cell is not None]
        if filtered_row:  # Chỉ thêm dòng nếu không rỗng
            data.append(filtered_row)
    rs = ''
    for row in data:
        for text in row:
            rs = rs + ' ' + str(text)
    return rs
