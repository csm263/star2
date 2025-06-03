import tkinter as tk
from tkinter import messagebox
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import webbrowser

# 🔐 Google Sheets 인증
json_path = 'C:/Users/pc/Desktop/mestar/checkmate-417613-ba4e43b15365.json'  # JSON 키 파일명 (같은 폴더에 위치)
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(json_path, scope)
client = gspread.authorize(creds)

# 📋 스프레드시트 이름 및 시트
SPREADSHEET_NAME = '이오스 쎈엽합 점수시트'
SHEET_NAME = '점수내역'
sheet = client.open(SPREADSHEET_NAME).worksheet(SHEET_NAME)

# 📌 다음 열 찾기
def get_next_column(sheet):
    existing_data = sheet.row_values(1)
    return len(existing_data) + 1

# 🔠 열 인덱스를 문자로 (A, B, ..., AA)
def get_column_letter(index):
    result = []
    while index > 0:
        index, remainder = divmod(index - 1, 26)
        result.append(chr(65 + remainder))
    return ''.join(reversed(result))

# ✅ 데이터 저장 함수
def 저장_데이터(결사부대원_목록, 선택된장소):
    if not 결사부대원_목록:
        messagebox.showerror("오류", "결사부대원 명단이 없습니다.")
        return

    결사부대원_문자열 = ', '.join(결사부대원_목록)
    저장시간 = datetime.now().strftime("%Y.%m.%d-%H.%M.%S")

    try:
        col_index = get_next_column(sheet)
        column_letter = get_column_letter(col_index)
        update_range = f"{column_letter}1:{column_letter}3"
        data = [[결사부대원_문자열], [저장시간], [선택된장소]]
        sheet.update(update_range, data)
        messagebox.showinfo("완료", f"✅ {선택된장소} 저장 완료!")
    except Exception as e:
        messagebox.showerror("오류 발생", str(e))

# 🪟 tkinter 윈도우
root = tk.Tk()
root.title("이오스 결사부대 기록기")
root.geometry("500x600")

# 📥 텍스트 입력창
tk.Label(root, text="🧑‍🤝‍🧑 결사부대원 명단 붙여넣기").pack()
text_input = tk.Text(root, height=10)
text_input.pack(pady=5)

# 🧭 장소 선택 함수
def on_place_click(place):
    content = text_input.get("1.0", tk.END).strip()
    lines = content.splitlines()
    members = []
    for line in lines:
        parts = line.split()
        if len(parts) > 1:
            members.append(parts[1])
    저장_데이터(members, place)

# 📍 장소 버튼들
장소들 = [
    "시틈보스", "으뜸자", "결사던전", "유니버스",
    "시틈메인타임", "쟁", "시틈봉인전", "농사본토보스"
]

tk.Label(root, text="📍 장소를 선택하세요:").pack(pady=(20, 5))
for 장소 in 장소들:
    btn = tk.Button(root, text=장소, command=lambda p=장소: on_place_click(p), width=20)
    btn.pack(pady=2)

# 📄 스펙조사 버튼
def open_google_form():
    url = "https://docs.google.com/forms/d/your-form-id"  # ← 여기에 설문 링크 입력
    webbrowser.open(url)

tk.Button(root, text="📋 스펙조사 설문지 열기", command=open_google_form, bg="lightblue").pack(pady=20)

# 앱 실행
root.mainloop()