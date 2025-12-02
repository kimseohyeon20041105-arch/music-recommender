import streamlit as st
from backend import recommend_knn, emotions
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ──────────────────────────────
# Google Sheets 저장 관련 함수
# ──────────────────────────────

def connect_to_gsheet():
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], scope
    )

    client = gspread.authorize(creds)

    # 시트 ID로 연결 (가장 안정적인 방식)
    sheet = client.open_by_key("10uxFwwOHTrZ5Hw1aUw_5M4JlKY-YZz8sRQ_X3NGTGeA").sheet1
    return sheet


def save_log_to_sheet(emo1, emo2, pop_level, recs):
    sheet = connect_to_gsheet()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for r in recs:
        sheet.append_row([
            timestamp,
            emo1,
            emo2 if emo2 else "",
            pop_level,
            r["title"],
            r["artist"],
            r["similarity"]
        ])

# ──────────────────────────────
# Streamlit UI
# ──────────────────────────────

st.set_page_config(page_title="감정 기반 음악 추천", page_icon="🎵")

st.title("🎵 감정 기반 음악 추천 시스템")

st.markdown("""
감정 목록: **happy, sad, relaxed, angry, focus, confident**  
pop_level: **0(60-70), 1(71-80), 2(81-99)**
""")

# 선택 입력
emo1 = st.selectbox("첫 번째 감정 선택", [""] + emotions)
emo2 = st.selectbox("두 번째 감정 선택(없어도 됨)", [""] + emotions)

pop_level = st.selectbox("인기도 레벨(pop_level)", [0, 1, 2])

if st.button("추천 받기"):
    if emo1 == "":
        st.warning("⚠ 첫 번째 감정을 반드시 선택해주세요.")
    else:
        user_emotions = [emo1]
        if emo2 != "":
            user_emotions.append(emo2)

        recs = recommend_knn(user_emotions, pop_level)

        # 🔥 구글 시트 저장
        save_log_to_sheet(emo1, emo2, pop_level, recs)
        st.success("✔ 추천 결과가 Google Sheets에 저장되었습니다!")

        st.subheader("🎶 추천 결과")
        for r in recs:
            st.write(f"- **{r['title']}** — *{r['artist']}*  (❗유사도 {r['similarity']})")

