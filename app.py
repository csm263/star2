import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

# 1) Secrets에서 순수 JSON 문자열(str) 꺼내기
json_content = st.secrets["gcp_service_account_json"]  # 이제 이 변수에 실질적인 JSON 문자열이 담깁니다.

# 2) /tmp/gcp_key.json 파일로 저장하고 환경 변수 지정
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/gcp_key.json"
with open("/tmp/gcp_key.json", "w", encoding="utf-8") as f:
    f.write(json_content)

# 3) Google Sheets 인증
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("/tmp/gcp_key.json", scope)
client = gspread.authorize(creds)

SPREADSHEET_NAME = "이오스 쎈엽합 점수시트"
SHEET_NAME = "점수내역"
sheet = client.open(SPREADSHEET_NAME).worksheet(SHEET_NAME)

# 3) Streamlit UI
st.set_page_config(page_title="결사부대원 입력", layout="centered")
st.title("📋 결사부대원 입력 및 저장")

# ———— 결사부대원 목록 입력 ————
members_input = st.text_area(
    "결사부대원 목록을 복사하여 붙여넣어주세요.\n\n"
    "- 예시:\n"
    "결사부대원 분대 1\n"
    "홍길동 32분대\n"
    "김철수 32분대\n"
    "…\n"
)
if not members_input.strip():
    st.info("결사부대원 목록을 입력하면, 아래에서 장소 선택 UI가 표시됩니다.")
    st.stop()

members_lines = members_input.splitlines()
결사부대원_목록 = []
is_member_section = False
for line in members_lines:
    if line.startswith("결사부대원 분대"):
        is_member_section = True
        continue
    if is_member_section and line.strip():
        parts = line.split()
        # “홍길동 32분대” → parts[0]에 “홍길동”이 들어왔다고 가정
        결사부대원_목록.append(parts[0])

if not 결사부대원_목록:
    st.error("❗ 제대로 된 결사부대원 목록이 감지되지 않았습니다. 다시 확인해 주세요.")
    st.stop()

결사부대원_문자열 = ", ".join(결사부대원_목록)
저장시간 = datetime.now().strftime("%Y.%m.%d-%H.%M.%S")

st.write(f"**✅ 결사부대원 목록이 입력되었습니다.** (총 {len(결사부대원_목록)}명)")
st.write(">" + 결사부대원_문자열)

# ———— 장소 선택 버튼 ————
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
        existing_header = sheet.row_values(1)
        col_index = len(existing_header) + 1

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
        st.success(f"✅ 장소 **{선택된장소}**가 선택되어 스프레드시트에 저장되었습니다.")
    except Exception as e:
        st.error(f"⚠️ 스프레드시트 업데이트 중 오류 발생:\n\n```\n{e}\n```")
    st.stop()

st.warning("아직 장소를 선택하지 않았습니다. 버튼을 눌러주세요!")
