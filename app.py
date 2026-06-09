import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Quiet Hero",
    page_icon="🔊",
    layout="centered"
)

# ------------------
# Session State
# ------------------

if "green_minutes" not in st.session_state:
    st.session_state.green_minutes = 0

if "reward" not in st.session_state:
    st.session_state.reward = False

# ------------------
# Header
# ------------------

st.title("🔊 Quiet Hero")
st.subheader("소란스러움 경고 앱")

st.markdown("""
### 사용 방법
현재 측정된 소음(dB)을 입력하세요.

색상 기준

- 🟢 초록 : 0~39 dB
- 🟡 노랑 : 40~54 dB
- 🟠 주황 : 55~69 dB
- 🔴 빨강 : 70 dB 이상

70 dB 이상일 때만 경고가 발생합니다.
""")

# ------------------
# Noise Input
# ------------------

noise = st.slider(
    "현재 소음 (dB)",
    min_value=0,
    max_value=120,
    value=30
)

# ------------------
# Status
# ------------------

if noise < 40:
    status = "🟢 초록"
    color = "#4CAF50"
    desc = "조용한 환경입니다."

elif noise < 55:
    status = "🟡 노랑"
    color = "#FFEB3B"
    desc = "약간의 생활 소음이 있습니다."

elif noise < 70:
    status = "🟠 주황"
    color = "#FF9800"
    desc = "다소 시끄러운 상태입니다."

else:
    status = "🔴 빨강"
    color = "#F44336"
    desc = "70dB 이상 소음이 감지되었습니다."

# ------------------
# Color Card
# ------------------

st.markdown(
    f"""
    <div style="
        background:{color};
        height:220px;
        border-radius:20px;
        display:flex;
        justify-content:center;
        align-items:center;
        font-size:40px;
        font-weight:bold;">
        {status}
    </div>
    """,
    unsafe_allow_html=True
)

st.write(desc)

# ------------------
# Warning
# ------------------

if noise >= 70:

    st.error("🚨 경고! 현재 소음이 70dB 이상입니다.")

    st.markdown(
        """
        <h1 style='text-align:center;color:red;'>
        🔇 조용히 해주세요!
        </h1>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <audio autoplay>
            <source src="https://www.soundjay.com/buttons/beep-01a.mp3" type="audio/mpeg">
        </audio>
        """,
        unsafe_allow_html=True
    )

# ------------------
# Quiet Time Reward
# ------------------

if noise < 40:
    st.session_state.green_minutes += 1

st.metric(
    "누적 조용한 시간",
    f"{st.session_state.green_minutes} 분"
)

if (
    st.session_state.green_minutes >= 45
    and not st.session_state.reward
):
    st.session_state.reward = True

if st.session_state.reward:

    st.success("🏆 보상 획득!")

    st.markdown("""
    ## 🌟 Quiet Hero 인증서

    45분 동안 조용한 환경을 유지했습니다.
    """)

    st.balloons()

# ------------------
# Statistics
# ------------------

st.divider()

st.subheader("📊 현재 정보")

st.write(f"현재 소음 : {noise} dB")
st.write(f"현재 상태 : {status}")
st.write(
    f"측정 시각 : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)

# ------------------
# Reset
# ------------------

if st.button("기록 초기화"):

    st.session_state.green_minutes = 0
    st.session_state.reward = False

    st.success("기록이 초기화되었습니다.")
