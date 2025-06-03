import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import streamlit as st

# ----------------------------------------
# ① 서비스 계정 JSON을 Secrets에서 바로 불러와 파싱
# ----------------------------------------
# Streamlit Cloud의 Settings → Secrets 탭에
# Key = gcp_service_account_json
# Value = 로컬 JSON 파일 내용 전체를 """..."""로 감싼 문자열
json_content = st.secrets["gcp_service_account_json"]

# JSON 문자열 → 파이썬 dict로 변환
info = json.loads(json_content)

# OAuth2 인증 범위 설정
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# from_json_keyfile_dict를 사용하여 바로 Credential 객체 생성
creds = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
client = gspread.authorize(creds)

# ----------------------------------------
# ② 스프레드시트 및 시트 열기
# ----------------------------------------
SPREADSHEET_NAME = "이오스 쎈엽합 점수시트"
SHEET_NAME = "점수내역"
sheet = client.open(SPREADSHEET_NAME).worksheet(SHEET_NAME)

# ----------------------------------------
# ③ Streamlit UI 구성
# ----------------------------------------
st.set_page_config(page_title="결사부대원 점수 입력", layout="centered")
st.title("📋 결사부대원 입력 및 저장")

# 1) 결사부대원 목록 입력
members_input = st.text_area(
    "결사부대원 목록을 복사하여 붙여넣어주세요.\n\n"
    "- 예시 양식:\n"
    "결사부대원 분대 1\n"
    "홍길동 32분대\n"
    "김철수 32분대\n"
    "…\n"
)

if not members_input.strip():
    st.info("결사부대원 목록을 입력하면, 아래에서 장소 선택 버튼이 활성화됩니다.")
    st.stop()

# 2) "결사부대원 분대" 이후 이름만 추출
members_lines = members_input.splitlines()
결사부대원_목록 = []
is_member_section = False

for line in members_lines:
    if line.startswith("결사부대원 분대"):
        is_member_section = True
        continue
    if is_member_section and line.strip():
        parts = line.split()
        if len(parts) >= 1:
            # 예: "홍길동 32분대" → parts[0] = "홍길동"
            결사부대원_목록.append(parts[0])

if not 결사부대원_목록:
    st.error("❗ 제대로 된 결사부대원 목록이 감지되지 않았습니다. 다시 확인해 주세요.")
    st.stop()

결사부대원_문자열 = ", ".join(결사부대원_목록)
저장시간 = datetime.now().strftime("%Y.%m.%d-%H.%M.%S")

st.write(f"**✅ 결사부대원 목록이 입력되었습니다.** (총 {len(결사부대원_목록)}명)")
st.write(">" + 결사부대원_문자열)

# ----------------------------------------
# ④ 장소 선택 버튼
# ----------------------------------------
st.write("---")
st.subheader("📍 장소를 선택해주세요")

col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)

선택된장소 = None
if col1.button("시틈보스"):
    선택된장소 = "시틈보스"
elif col2.button("으뜸자"):
    선택된장소 = "으뜸자"
elif col3.button("결사던전"):
    선택된장소 = "결사던전"
elif col4.button("유니버스"):
    선택된장소 = "유니버스"
elif col5.button("시틈메인타임"):
    선택된장소 = "시틈메인타임"
elif col6.button("쟁"):
    선택된장소 = "쟁"

if 선택된장소:
    try:
        # 1행(헤더)에 이미 있는 열 개수 가져오기
        existing_header = sheet.row_values(1)
        col_index = len(existing_header) + 1

        # 숫자 → 스프레드시트 열 문자(A, B, C...) 변환 함수
        def get_column_letter(idx: int) -> str:
            result = []
            while idx > 0:
                idx, rem = divmod(idx - 1, 26)
                result.append(chr(65 + rem))
            return "".join(reversed(result))

        column_letter = get_column_letter(col_index)
        update_range = f"{column_letter}1:{column_letter}3"
        data_to_update = [
            [결사부대원_문자열],
            [저장시간],
            [선택된장소]
        ]
        sheet.update(update_range, data_to_update)
        st.success(f"✅ 장소 **'{선택된장소}'**가 선택되어 스프레드시트에 저장되었습니다.")
    except Exception as e:
        st.error(f"⚠️ 스프레드시트 업데이트 중 오류가 발생했습니다:\n\n```\n{e}\n```")
    st.stop()

st.warning("아직 장소를 선택하지 않았습니다. 위 버튼 중 하나를 눌러주세요!")

# 📄 스펙조사 버튼
def open_google_form():
    url = "https://forms.gle/B5nsHGkMin1BLC9r5"  # ← 여기에 설문 링크 입력
    webbrowser.open(url)

tk.Button(root, text="📋 스펙조사 설문지 열기", command=open_google_form, bg="lightblue").pack(pady=20)

# 앱 실행
root.mainloop()
