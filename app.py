import streamlit as st
import numpy as np
import pandas as pd
import time
from streamlit_mic_recorder import mic_recorder

st.set_page_config(
    page_title="교실 소음 신호등",
    page_icon="🚦",
    layout="wide"
)

st.title("🚦 교실 소음 신호등")
st.markdown("학생들의 소음을 실시간으로 측정합니다.")

# 세션 상태 초기화
if "history" not in st.session_state:
    st.session_state.history = []

if "quiet_start" not in st.session_state:
    st.session_state.quiet_start = None

if "warning_count" not in st.session_state:
    st.session_state.warning_count = 0


def calculate_db(audio_bytes):
    try:
        audio_array = np.frombuffer(audio_bytes, dtype=np.int16)

        if len(audio_array) == 0:
            return 0

        rms = np.sqrt(np.mean(audio_array.astype(np.float64) ** 2))

        if rms <= 0:
            return 0

        db = 20 * np.log10(rms)
        return round(float(db), 1)

    except Exception:
        return 0


st.subheader("🎤 소음 측정")

audio = mic_recorder(
    start_prompt="측정 시작",
    stop_prompt="측정 완료",
    key="noise_recorder"
)

if audio:

    try:
        audio_bytes = audio["bytes"]

        db = calculate_db(audio_bytes)

        st.metric("현재 소음 수준", f"{db} dB")

        st.session_state.history.append(
            {
                "시간": time.strftime("%H:%M:%S"),
                "dB": db
            }
        )

        # 신호등 상태
        if db < 45:
            color = "🟢"
            state = "조용함"

            if st.session_state.quiet_start is None:
                st.session_state.quiet_start = time.time()

        elif db < 60:
            color = "🟡"
            state = "주의"

            st.session_state.quiet_start = None

        else:
            color = "🔴"
            state = "시끄러움"

            st.session_state.quiet_start = None

            st.audio(
                "https://www.soundjay.com/buttons/beep-01a.mp3"
            )

        st.markdown(
            f"""
            # {color} {state}
            """
        )

        # 50분 조용함 유지
        if st.session_state.quiet_start:

            elapsed = time.time() - st.session_state.quiet_start

            remain = max(0, 3000 - elapsed)

            st.info(
                f"칭찬까지 남은 시간 : {int(remain // 60)}분"
            )

            if elapsed >= 3000:
                st.success("🎉 50분 동안 조용했습니다! 정말 훌륭해요!")
                st.balloons()

    except Exception as e:
        st.error(f"오류 발생: {e}")

# 그래프
if len(st.session_state.history) > 0:

    st.subheader("📈 소음 변화")

    df = pd.DataFrame(st.session_state.history)

    st.line_chart(df["dB"])

    st.dataframe(df, use_container_width=True)

# 기준 안내
st.divider()

st.subheader("📋 소음 기준")

st.markdown("""
- 🟢 45 dB 미만 : 조용함
- 🟡 45 ~ 60 dB : 주의
- 🔴 60 dB 이상 : 시끄러움
""")
