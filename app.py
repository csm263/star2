import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import streamlit as st

# ----------------------------------------
# ① Streamlit Cloud용 서비스 계정 JSON 불러오기
# ----------------------------------------
# Streamlit Cloud 대시보드의 "Settings → Secrets" 탭에
# Key = gcp_service_account_json
# Value = (로컬 JSON 파일 내용 전체)를 넣어두었다고 가정합니다.

json_content = st.secrets["gcp_service_account_json"]
# Streamlit Cloud는 일반적으로 /tmp 같은 경로에 파일을 써서 사용합니다.
# 아래는 임시 경로에 JSON을 저장하고, GOOGLE_APPLICATION_CREDENTIALS 환경 변수를 지정하는 예시입니다.
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/gcp_key.json"
with open("/tmp/gcp_key.json", "w", encoding="utf-8") as f:
    f.write(json_content)

# ----------------------------------------
# ② Google Sheets 인증 및 시트 열기
# ----------------------------------------
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("/tmp/gcp_key.json", scope)
client = gspread.authorize(creds)

# 스프레드시트 및 시트 이름 설정
SPREADSHEET_NAME = "이오스 쎈엽합 점수시트"
SHEET_NAME = "점수내역"
sheet = client.open(SPREADSHEET_NAME).worksheet(SHEET_NAME)

# ----------------------------------------
# ③ Streamlit 화면 구성
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

# 입력이 비어 있으면 아래 안내 메시지만 보여주고 종료
if not members_input.strip():
    st.info("결사부대원 목록을 입력하면, 아래에서 장소 선택 버튼이 활성화됩니다.")
    st.stop()

# 2) 입력된 텍스트에서 "결사부대원 분대" 이후의 이름들만 추출
members_lines = members_input.splitlines()
결사부대원_목록 = []
is_member_section = False

for line in members_lines:
    if line.startswith("결사부대원 분대"):
        is_member_section = True
        continue
    if is_member_section and line.strip():
        parts = line.split()
        # "김철수 32분대" 식으로 스페이스로 구분되어 있으면 parts[0]이 이름(parts[1]이 분대)
        # 예시 코드에서는 이름을 parts[0]으로, 분대는 parts[1]으로 생각했지만
        # 실제로는 사용자가 입력한 양식에 맞춰서 다음처럼 조정합니다:
        # (원래 예시: parts[1]을 결사부대원으로 썼는데, 화면 양식에 따라 변경)
        if len(parts) >= 1:
            # 예시에서는 두 칸짜리여서 parts[1]이 이름이었지만, 아래는
            # “이름(공백)분대” 형태이므로, 이름만 남기는 로직으로 수정하세요.
            # 예: "홍길동 32분대" → parts[0] = "홍길동", parts[1] = "32분대"
            결사부대원_목록.append(parts[0])

if not 결사부대원_목록:
    # 추출된 목록이 비어 있다면 오류 메시지 출력 후 종료
    st.error("❗ 제대로 된 결사부대원 목록이 감지되지 않았습니다. 다시 확인해 주세요.")
    st.stop()

# 결사부대원 정보를 한 줄 문자열로 만듦 (가로로 이어 붙여서)
결사부대원_문자열 = ", ".join(결사부대원_목록)
저장시간 = datetime.now().strftime("%Y.%m.%d-%H.%M.%S")

# 화면에 추출된 결사부대원 목록 확인 용으로 출력
st.write(f"**✅ 결사부대원 목록이 입력되었습니다.** (총 {len(결사부대원_목록)}명)")
st.write(">" + 결사부대원_문자열)

# ----------------------------------------
# ④ 장소 선택 버튼 보여주기
# ----------------------------------------
st.write("---")
st.subheader("📍 장소를 선택해주세요")

# 6개의 버튼을 2행 × 3열로 배치
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

# 누른 버튼이 있으면 아래에서 스프레드시트에 기록
if 선택된장소:
    try:
        # 스프레드시트의 1행(헤더) 기준으로, 현재 사용된 열 개수를 구함
        existing_header = sheet.row_values(1)
        col_index = len(existing_header) + 1

        # 숫자(열 인덱스)를 스프레드시트 열 문자(A, B, C, ...)로 바꾸는 함수
        def get_column_letter(idx: int) -> str:
            result = []
            while idx > 0:
                idx, rem = divmod(idx - 1, 26)
                result.append(chr(65 + rem))
            return "".join(reversed(result))

        column_letter = get_column_letter(col_index)
        update_range = f"{column_letter}1:{column_letter}3"
        data_to_update = [
            [결사부대원_문자열],  # 1행: 결사부대원 문자열
            [저장시간],          # 2행: 저장 시간
            [선택된장소]         # 3행: 선택된 장소
        ]
        sheet.update(update_range, data_to_update)
        st.success(f"✅ 장소 **'{선택된장소}'**가 선택되어 스프레드시트에 저장되었습니다.")
    except Exception as e:
        st.error(f"⚠️ 스프레드시트 업데이트 중 오류가 발생했습니다:\n\n```\n{e}\n```")
    # 기록이 끝났으므로 더 이상 아래 로직은 실행하지 않고 종료
    st.stop()

# 버튼은 눌리지 않은 상태라면 안내 메시지 출력
st.warning("아직 장소를 선택하지 않았습니다. 위 버튼 중 하나를 눌러주세요!")

# 📄 스펙조사 버튼
def open_google_form():
    url = "https://docs.google.com/forms/d/your-form-id"  # ← 여기에 설문 링크 입력
    webbrowser.open(url)

tk.Button(root, text="📋 스펙조사 설문지 열기", command=open_google_form, bg="lightblue").pack(pady=20)

# 앱 실행
root.mainloop()
