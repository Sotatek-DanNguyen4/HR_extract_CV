from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from datetime import datetime
import re
import json
current_time = datetime.now()
def merge_periods(periods):
    # Sort periods based on start date
    periods = sorted(periods, key=lambda x: x[0])

    merged = []
    current_start, current_end = periods[0]

    for start, end in periods[1:]:
        if start <= current_end:
            # Merge overlapping periods
            current_end = max(current_end, end)
        else:
            merged.append((current_start, current_end))
            current_start, current_end = start, end

    merged.append((current_start, current_end))
    return merged
# Định dạng thời gian thành MM/YYYY
formatted_time = current_time.strftime("%m/%Y")
def calculate_total_working_time(job_data):
    total_months = 0
    periods = []
    for period in job_data.values():
        period = period.replace('present', str(formatted_time))
        period = period.replace('Present', str(formatted_time))
        period = period.replace('PRESENT', str(formatted_time))
        period = period.replace('Now', str(formatted_time))
        try:
            start, end = period.split(' - ')
        except:
            start = '2024'
            end = '2024'
        if len(start) == 4:
            start = f"01/{start}"
        elif len(start) == 7 and start[4] == '/':  # YYYY/MM
            start = start[5:] + '/' + start[:4]  # MM/YYYY
        elif len(start) > 8:
            start = start[-7:]
        if len(end) == 4:
            end = f"01/{end}"
        elif len(end) == 7 and end[4] == '/':  # YYYY/MM
            end = end[5:] + '/' + end[:4]  # MM/YYYY
        elif len(end) > 8:
            end = end[-7:]
        start_date = datetime.strptime(start, '%m/%Y')
        end_date = datetime.strptime(end, '%m/%Y')

        periods.append((start_date, end_date))
    merged_periods = merge_periods(periods)
    for start, end in merged_periods:
        months_worked = (end.year - start.year) * 12 + (end.month - start.month)
        total_months += months_worked

    years_in_decimal = total_months / 12
    return round(years_in_decimal, 1)
def extract_field(text):
    chat = ChatGroq(
        temperature=0,
        model="llama3-70b-8192",
        # api_key="" # Optional if not set as an environment variable mixtral-8x7b-32768
    )

    chat_32k = ChatGroq(
        temperature=0,
        model="mixtral-8x7b-32768",
        # api_key="" # Optional if not set as an environment variable mixtral-8x7b-32768
    )

    system = """Bạn là một trợ lý hỗ trợ trích xuất các trường thông tin trong CV của ứng viên, trả lời bằng TIẾNG VIỆT.
                Trích xuất ra bằng Tiếng việt các thông tin sau: tên(nếu tên không có dấu thì vẫn giữ nguyên), giới tính, email, số điện thoại, địa chỉ,trường đại học, bằng cấp ( chỉ trả ra giỏi, khá, hoặc trung bình),GPA(chỉ lấy điểm số trung bình tốt nghiệp) chứng chỉ(bao gồm các loại chứng chỉ, chứng nhận). Nếu không có thông tin thì trả ra 'Không'. Chỉ cần đưa ra đáp án là dạng json, không cần giải thích gì thêm.
                Các trường thông tin có Ngôn ngữ khác tiếng việt thì dịch ra tiếng việt và điền vào đó.
                Kết quả trả ra dưới dạng JSON, các value đều phải là dạng string.
                Dưới đây là một số ví dụ:
                Ví dụ 1:
                "Tên": "Nguyen Van Long"
                "Giới tính": "Nam"
                "Email": "longnguyen@gmail.com"
                "Số điện thoại": "0342235612"
                "Địa chỉ": "Ba Đình- Hà Nội"
                "Trường đại học": "Bách Khoa"
                "Bằng cấp": "Không"
                "GPA": "Không"
                "Chứng chỉ chuyên ngành": "M2M BA: Business Analysis, LinkedIn: Power BI Essential Training"
                "Chứng chỉ ngoại ngữ": "Tiếng Nhật N1, Tiếng Anh B2"
                Ví dụ 2:
                "Tên": "Vũ Như Hòa"
                "Giới tính": "Nữ"
                "Email": "hoanguyen45@gmail.com"
                "Số điện thoại": "0334735612"
                "Địa chỉ":"Không"
                "Trường đại học": "Đại học Xây dựng"
                "Bằng cấp": "Khá"
                "GPA": "2.84"
                "Chứng chỉ chuyên ngành": " AWS Certified Solutions Architect – Professional"
                "Chứng chỉ ngoại ngữ": "Tiếng Anh Ielts 8.0"
                Dưới đây là đoạn văn cần trích xuất:
                """
    system_work = """Bạn là một trợ lý hỗ trợ trích xuất các trường thông tin kinh nghiệm làm việc trong CV của ứng viên bằng cách trả ra tất cả tên công ty và thời gian làm việc tương ứng, trả ra dạng Json theo định dạng: key là "tên công ty, vị trí làm việc" value là "tháng/năm - tháng/năm", biết hiện tại là {time}, hãy thay thế 'Present' hoặc 'hiện tại' và các từ tương đương là {time}
            Lưu ý: thời gian bắt đầu và kết thúc luôn phải là dạng MM/YYYY, kết quả trả ra bắt buộc phải đầy đủ thời gian bắt đầu và thời gian kết thúc, nếu thiếu thông tin thời gian bắt đầu, hãy lấy thời gian bắt đầu là thời điểm hiện tại.
            Nếu tháng viết bằng chữ, cần chuyển về dạng số.
            Kết quả phải là dạng json
            Ví dụ:
            ---
            "VVCC, developer": "01/2021 - 03/2022",
            "VVCC, sale": "01/2023 - 06/2023",
            "vincom, dev": "06/2023 -  08/2024"
            ---
            "VCC, BA": "11/2002 - 03/2007",
            "CVB, design": "07/2012 - 05/2019",
            "công ty abc, vị trí": "11/2021 - 12/2022"
            Dưới đây là thông tin CV:
            """
    try:
        system_work = system_work.format(time=formatted_time)
        system = system.format(time=formatted_time)
        human = "{text}"
        prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])
        prompt_work = ChatPromptTemplate.from_messages([("system", system_work), ("human", human)])

        chain = prompt | chat
        # res_extracted=chain.invoke({"text": text}).content
        res_extracted=chat.invoke(system+text).content
        # print(res_extracted)
        chain_work = prompt_work | chat
        # res_extracted_work=chain_work.invoke({"text": text}).content
        res_extracted_work=chat.invoke(system_work+text).content
        # print(res_extracted_work)
        result = re.search(r'\{.*?\}', res_extracted, re.DOTALL).group()
        json_object = json.loads(result)
        try:
            result_work = re.search(r'\{.*?\}', res_extracted_work, re.DOTALL).group()
            json_object_work = json.loads(result_work)
            # print(json_object_work)
            years = calculate_total_working_time(json_object_work)
        except:
            years=0
        text_output =''
        for key, value in json_object.items():
            if key == 'Chứng chỉ chuyên ngành':
                if 'HTML' in value or 'PHP' in value or 'CSS' in value or 'MySQL' in value or 'Java' in value or 'EXCEL' in value:
                    value = 'Không'
            text_output += f"{key}: {value}\n"
        text_output = text_output+ 'Kinh nghiệm làm việc: '+str(years)+ ' năm '
    except:
        print('switch to 32k...')
        chat = ChatGroq(
        temperature=0,
        model="mixtral-8x7b-32768",)
        # api_key="" # Optional if not set as an environment variable mixtral-8x7b-32768
        system_work = system_work.format(time=formatted_time)
        system = system.format(time=formatted_time)
        human = "{text}"
        prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])
        prompt_work = ChatPromptTemplate.from_messages([("system", system_work), ("human", human)])

        chain = prompt | chat
        # res_extracted=chain.invoke({"text": text}).content
        res_extracted=chat.invoke(system+text).content
        print(res_extracted)
        chain_work = prompt_work | chat
        # res_extracted_work=chain_work.invoke({"text": text}).content
        res_extracted_work=chat.invoke(system_work+text).content
        # print(res_extracted_work)
        result = re.search(r'\{.*?\}', res_extracted, re.DOTALL).group()
        json_object = json.loads(result)
        try:
            result_work = re.search(r'\{.*?\}', res_extracted_work, re.DOTALL).group()
            json_object_work = json.loads(result_work)
            print(json_object_work)
            years = calculate_total_working_time(json_object_work)
        except:
            years=0
        text_output =''
        for key, value in json_object.items():
            if key == 'Chứng chỉ chuyên ngành':
                if 'HTML' in value or 'PHP' in value or 'CSS' in value or 'MySQL' in value or 'Java' in value or 'EXCEL' in value:
                    value = 'Không'
            text_output += f"{key}: {value}\n"
        text_output = text_output+ 'Kinh nghiệm làm việc: '+str(years)+ ' năm '

    return text_output
