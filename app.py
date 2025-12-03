import streamlit as st
from backend import recommend_knn, emotions
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import random
import string

# ──────────────────────────────
# 사용자 ID 생성 (짧은 6자리)
# ──────────────────────────────
if "user_id" not in st.session_state:
    st.session_state.user_id = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

# ──────────────────────────────
# Google Sheets 연결 함수
# ──────────────────────────────
def connect_to_gsheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], scope
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key("10uxFwwOHTrZ5Hw1aUw_5M4JlKY-YZz8sRQ_X3NGTGeA").sheet1
    return sheet


def save_to_sheet(recs, emo1, emo2, pop_level, rating=None, mood_after=None, comment=""):
    sheet = connect_to_gsheet()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_id = st.session_state.user_id

    for r in recs:
        sheet.append_row([
            timestamp,
            user_id,
            emo1,
            emo2 if emo2 else "",
            pop_level,
            r["title"],
            r["artist"],
            r["similarity"],
            rating if rating else "",
            mood_after if mood_after else "",
            comment
        ])

# ──────────────────────────────
# Streamlit UI
# ──────────────────────────────

st.set_page_config(page_title="감정 기반 음악 추천", page_icon="🎵")

# 모바일 반응형 CSS 포함
st.markdown("""
<style>
/* 전체 레이아웃 여백 조정 */
.main, .block-container {
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

/* 글자가 박스 밖으로 튀어나가는 현상 방지 */
* {
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
    white-space: normal !important;
}

/* 배경색 / 글자색 고정 */
body, .block-container {
    background-color: #ffffff !important;
    color: #000000 !important;
}

a {
    color: #0066CC !important;
}

/* 박스 스타일 */
.cute-box {
    padding: 15px 18px;
    border-radius: 15px;
    font-size: 17px;
    line-height: 1.5;
    background-color: #D9F1FF !important;
    color: #000000 !important;
}

.colored-box {
    background-color: #D9F1FF !important;
    color: #000000 !important;
}

/* 텍스트 스타일 */
.title-text {
    font-size: 20px;
    font-weight: 600;
    color: #000000 !important;
}

/* 제목은 박스 밖에서 독립 */
.title-main {
    font-size: 35px;
    font-weight: 700;
    background: linear-gradient(90deg, #6EE888, #9EFFA4, #C9FFC8);
    -webkit-background-clip: text;
    color: transparent;
    text-shadow: 0px 2px 12px rgba(0,0,0,0.15);
    text-align: center;
    margin-bottom: 15px;
}

/* 구분선 텍스트 */
.divider-text {
    font-size: 14px;
    color: #777 !important;
}

/* 모바일 화면 대응 */
@media screen and (max-width: 600px) {

    .cute-box {
        padding: 12px 14px !important;
        font-size: 14px !important;
        line-height: 1.4 !important;
    }

    .title-text {
        font-size: 15px !important;
    }

    .title-main {
        font-size: 22px !important;
        line-height: 1.2 !important;
        padding: 0 6px !important;
    }

    .divider-text {
        font-size: 11px !important;
    }

    .stSelectbox label, .stRadio label {
        font-size: 14px !important;
    }

    textarea, input {
        font-size: 14px !important;
    }
}
</style>
""", unsafe_allow_html=True)

# 소개 박스
st.markdown(
    """
<div class="cute-box">
    <div class="title-main"> ✧ ♪˚₊· 감정 기반 음악 추천 시스템 ·₊˚♪ ✧</div><br>
    지금 감정에 따라 지금 딱 맞는 음악을 추천받아보세요! <br>
    선택한 감정과 인기도(pop_level)를 기반으로 영어 음악을 추천해주는 시스템입니다. 
</div>
<br>
""",
    unsafe_allow_html=True
)

# 감정 안내 박스
st.markdown(
    """
<div class="cute-box colored-box">
    <div class="title-text">✔ 선택 가능한 감정</div>
    happy · sad · relaxed · angry · focus · confident
</div>

<br>

<div class="cute-box colored-box">
    <div class="title-text">✷ 인기도 (pop_level)</div>
    0 : 60-70<br>
    1 : 71–80<br>
    2 : 81–99
</div>
<br>
""",
    unsafe_allow_html=True
)

# 안내 박스
st.markdown(
    """
<div class="cute-box">
    지금 내 분위기에 딱 맞는 음악을 추천받아보세요 ⋆⁺₊⋆
</div>
""",
    unsafe_allow_html=True
)

# 입력 UI
emo1 = st.selectbox("첫 번째 감정 선택", [""] + emotions)
emo2 = st.selectbox("두 번째 감정 선택(없어도 됨)", [""] + emotions)
pop_level = st.selectbox("인기도 레벨(pop_level)", [0, 1, 2])

# 추천 버튼
if st.button("추천 받기"):
    if emo1 == "":
        st.warning("⚠ 첫 번째 감정을 반드시 선택해주세요.")
    else:
        user_emotions = [emo1] + ([emo2] if emo2 else [])
        st.session_state.recs = recommend_knn(user_emotions, pop_level)
        st.session_state.emo1 = emo1
        st.session_state.emo2 = emo2
        st.session_state.pop_level = pop_level

        st.success("추천이 생성되었어요!")

# 추천 결과 + 피드백
if "recs" in st.session_state:
    st.subheader("✧♬˚₊· 추천 결과")

    for r in st.session_state.recs:
        st.markdown(
            f"- **[{r['title']}]({r['spotify_url']})** — *{r['artist']}* ",
            unsafe_allow_html=True
        )


    # 구분선
    st.markdown(
        """
        <div style="display:flex; align-items:center; margin:20px 0;">
            <div style="flex-grow:1; height:1px; background:#ccc;"></div>
            <div class="divider-text" style="padding:0 10px;">
                ✦⋆˙✧₊˚༉‧₊˚⋆⁺₊⋆✧˙⋆✦
            </div>
            <div style="flex-grow:1; height:1px; background:#ccc;"></div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 자동 저장
    save_to_sheet(
        st.session_state.recs,
        st.session_state.emo1,
        st.session_state.emo2,
        st.session_state.pop_level
    )

    # 피드백 섹션
    st.markdown(
        """
        <p style="font-size:24px; font-weight:600;">
            <span style="color:#FF4B4B;">✎</span>
            <span style="color:#000000;">추천 피드백을 남겨주세요!</span>
        </p>
        """,
        unsafe_allow_html=True
    )

    rating = st.slider("추천 만족도 (1~5)", 1, 5, 3)

    mood_after = st.radio(
        "추천 후 기분 변화는?",
        ["더 좋아졌어요 🙂", "그대로예요 😐", "별로였어요 🙁"]
    )

    st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)

    comment = st.text_area(
        "문의사항이나 의견을 남겨주세요 (선택사항)",
        placeholder="ex. 오늘 감정이랑 너무 잘 맞았어요!"
    )

    if st.button("피드백 제출"):
        save_to_sheet(
            st.session_state.recs,
            st.session_state.emo1,
            st.session_state.emo2,
            st.session_state.pop_level,
            rating,
            mood_after,
            comment
        )
        st.success("⋆₊˚ෆ 피드백이 반영되었어요. 더 나은 음악을 추천할게요 ෆ˚₊⋆")
