import streamlit as st
import time
from datetime import datetime

st.set_page_config(
    page_title="Quiet Hero",
    page_icon="🔊",
    layout="centered"
)

# -------------------------
# 세션 상태 초기화
# -------------------------

if "green_seconds" not in st.session_state:
    st.session_state.green_seconds = 0

if "reward_given" not in st.session_state:
    st.session_state.reward_given = False

if "noise_level" not in st.session_state:
    st.session_state.noise_level = 0

# -------------------------
# 제목
# -------------------------

st.title("🔊 Quiet Hero")
st.subheader("소란스러움 경고 앱")

st.markdown("""
현재 소란스러움 정도를 입력하여 상태를 확인하세요.

실제 마이크 측정은 브라우저 보안 문제로
Streamlit Cloud에서 안정적으로 동작하기 어렵기 때문에
가장 오류 없는 방식으로 구현했습니다.
""")

# -------------------------
# 소음 입력
# -------------------------

noise = st.slider(
    "현재 소란스러움 지수",
    min_value=0,
    max_value=100,
    value=30
)

st.session_state.noise_level = noise

# -------------------------
# 상태 판정
# -------------------------

status = ""
color = ""
message = ""

if noise < 25:
    status = "초록"
    color = "#4CAF50"
    message = "매우 조용합니다."
elif noise < 50:
    status = "노랑"
    color = "#FFEB3B"
    message = "조금 소란스럽습니다."
elif noise < 75:
    status = "주황"
    color = "#FF9800"
    message = "시끄러운 상태입니다."
else:
    status = "빨강"
    color = "#F44336"
    message = "매우 시끄럽습니다!"

# -------------------------
# 색상 카드
# -------------------------

st.markdown(
    f"""
    <div style="
        background-color:{color};
        height:180px;
        border-radius:20px;
        display:flex;
        align-items:center;
        justify-content:center;
        font-size:42px;
        font-weight:bold;
        color:black;">
        {status}
    </div>
    """,
    unsafe_allow_html=True
)

st.write(message)

# -------------------------
# 경고음
# -------------------------

if status == "빨강":

    st.error("🚨 소음이 너무 큽니다!")

    st.markdown("""
    <audio autoplay>
      <source src="https://www.soundjay.com/buttons/beep-01a.mp3" type="audio/mpeg">
    </audio>
    """,
    unsafe_allow_html=True)

# -------------------------
# 조용한 시간 누적
# -------------------------

if status == "초록":
    st.session_state.green_seconds += 60

minutes = st.session_state.green_seconds // 60

st.metric(
    "누적 조용한 시간",
    f"{minutes} 분"
)

# -------------------------
# 보상
# -------------------------

if (
    st.session_state.green_seconds >= 2700
    and not st.session_state.reward_given
):
    st.session_state.reward_given = True

if st.session_state.reward_given:

    st.success("🏆 보상 획득!")
    st.balloons()

    st.markdown("""
    ## 🌟 Quiet Hero 인증

    45분 동안 조용한 환경을 유지했습니다!
    """)

# -------------------------
# 통계
# -------------------------

st.divider()

st.subheader("📊 오늘의 상태")

st.write(f"현재 소란스러움 지수 : {noise}")
st.write(f"현재 상태 : {status}")
st.write(f"측정 시간 : {datetime.now().strftime('%H:%M:%S')}")

# -------------------------
# 리셋
# -------------------------

if st.button("기록 초기화"):

    st.session_state.green_seconds = 0
    st.session_state.reward_given = False

    st.success("초기화 완료")
