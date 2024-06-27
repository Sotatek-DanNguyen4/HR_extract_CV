from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
def extract_field(text):
    chat = ChatGroq(
        temperature=0,
        model="llama3-70b-8192",
        # api_key="" # Optional if not set as an environment variable
    )

    system = """Bạn là một trợ lý hỗ trợ trích xuất các trường thông tin trong CV của ứng viên, trả lời bằng TIẾNG VIỆT.
                Trích xuất ra bằng Tiếng việt các thông tin sau: tên(nếu tên không có dấu thì vẫn giữ nguyên),ngày tháng năm sinh, giới tính, email, số điện thoại, địa chỉ,trường đại học, bằng cấp ( chỉ trả ra giỏi, khá, hoặc trung bình).Nếu không có thông tin thì trả ra 'Không'.
                Các trường thông tin có Ngôn ngữ khác tiếng việt thì dịch ra tiếng việt và điền vào đó thôi.
                Dưới đây là một số ví dụ:
                Ví dụ 1: "Tên: Nguyen Van Long
                Giới tính: Nam
                Email: longnguyen@gmail.com
                Số điện thoại: 0342235612
                Địa chỉ: Ba Đình- Hà Nội
                Trường đại học: Bách Khoa
                Bằng cấp: Không",
                Ví dụ 2: "Tên: Vũ Như Hòa
                Giới tính: Nữ
                Email: hoanguyen45@gmail.com
                Số điện thoại: 0334735612
                Địa chỉ: Không
                Trường đại học: Đại học Xây dựng
                Bằng cấp: Khá ",
                Dưới đây là đoạn văn cần trích xuất:"""
    human = "{text}"
    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

    chain = prompt | chat
    res_extracted=chain.invoke({"text": text}).content
    return res_extracted