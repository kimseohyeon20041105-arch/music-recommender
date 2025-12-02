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

    # ✔ 시트 ID 방식으로 연결 (이 방식이 가장 안정적)
    sheet = client.open_by_key("10uxFwwOHTrZ5Hw1aUw_5M4JlKY-YZz8sRQ_X3NGTGeA").sheet1
    return sheet


def save_log_to_sheet(emo1, emo2, pop_level, recs, rating=None, mood_after=None):
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
            r["similarity"],
            rating if rating is not None else "",
            mood_after if mood_after is not None else ""
        ])


# ──────────────────────────────
# Streamlit UI
# ──────────────────────────────

st.set_page_config(page_title="감정 기반 음악 추천", page_icon="🎵")

st.markdown("""
    <style>
        .cute-box {
            padding: 15px 18px;
            border-radius: 15px;
            font-size: 17px;
            line-height: 1.5;
        }
        .colored-box {
            background-color: #D9F1FF;
        }
        .title-text {
            font-size: 20px;
            font-weight: 600;
        }
    </style>
""", unsafe_allow_html=True)

# 상단 소개 박스
st.markdown(
    """
<div class="cute-box">
    <div class="title-text">🎵 감정 기반 음악 추천 시스템</div>
    지금 감정에 따라 지금 딱 맞는 음악을 추천받아보세요! 💜<br>
    선택한 감정과 인기도(pop_level)를 기반으로 영어 음악을 추천해주는 시스템입니다. 🎧  
</div>

<br>
""",
    unsafe_allow_html=True
)

# 감정 안내 박스
st.markdown(
    """
<div class="cute-box colored-box">
    <div class="title-text">✅ 선택 가능한 감정</div>
    happy · sad · relaxed · angry · focus · confident
</div>

<br>

<div class="cute-box colored-box">
    <div class="title-text">🔥 인기도 (pop_level)</div>
    0 : 60–70<br>
    1 : 71–80<br>
    2 : 81–99
</div>

<br>
""",
    unsafe_allow_html=True
)

st.markdown(
    """
<div class="cute-box">
    지금 내 분위기에 딱 맞는 음악을 찾아보자! 🌈    
</div>
""",
    unsafe_allow_html=True
)

# 선택 입력
emo1 = st.selectbox("첫 번째 감정 선택", [""] + emotions)
emo2 = st.selectbox("두 번째 감정 선택(없어도 됨)", [""] + emotions)
pop_level = st.selectbox("인기도 레벨(pop_level)", [0, 1, 2])

# ──────────────────────────────
# 추천 버튼
# ──────────────────────────────
if st.button("추천 받기"):
    if emo1 == "":
        st.warning("⚠ 첫 번째 감정을 반드시 선택해주세요.")
    else:
        user_emotions = [emo1]
        if emo2 != "":
            user_emotions.append(emo2)

        # 추천 실행
        recs = recommend_knn(user_emotions, pop_level)

        # 추천 결과 출력
        st.subheader("🎶 추천 결과")
        for r in recs:
            st.write(f"- **{r['title']}** — *{r['artist']}*  (❗유사도 {r['similarity']})")

        # 🔥 추천 결과 Google Sheets 자동 저장 (피드백 없이도 기록됨)
        save_log_to_sheet(emo1, emo2, pop_level, recs)

        # ──────────────────────────────
        # ⭐ + 🙂 피드백 UI (추천 후에만 표시!)
        # ──────────────────────────────
        st.subheader("📝 추천에 대한 피드백을 남겨주세요!")

        rating = st.slider("이번 추천 만족도는? (1 = 별로, 5 = 최고)", 1, 5, 3)

        mood_after = st.radio(
            "추천을 들은 후 기분이 어떻게 변했나요?",
            ["더 좋아졌어요 🙂", "그대로예요 😐", "별로였어요 🙁"]
        )

        if st.button("피드백 제출"):
            save_log_to_sheet(emo1, emo2, pop_level, recs, rating, mood_after)
            st.success("피드백이 저장되었습니다! 💜 고마워요!")


