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
st.write("녹음한 소리를 분석하여 교실 소음 수준을 표시합니다.")

# 세션 상태
if "history" not in st.session_state:
    st.session_state.history = []

if "quiet_count" not in st.session_state:
    st.session_state.quiet_count = 0

# 소음 계산 함수
def calculate_noise(audio_bytes):
    try:
        audio = np.frombuffer(audio_bytes, dtype=np.int16)

        if len(audio) == 0:
            return 0

        rms = np.sqrt(np.mean(audio.astype(np.float64) ** 2))

        if rms <= 0:
            return 0

        db = 20 * np.log10(rms)

        return round(db, 1)

    except Exception:
        return 0

st.subheader("🎤 소음 측정")

audio = mic_recorder(
    start_prompt="🎙️ 녹음 시작",
    stop_prompt="⏹️ 녹음 종료",
    key="noise"
)

if audio is not None:

    try:

        audio_bytes = audio.get("bytes")

        if audio_bytes:

            db = calculate_noise(audio_bytes)

            st.metric("현재 소음 수준", f"{db} dB")

            now = time.strftime("%H:%M:%S")

            st.session_state.history.append({
                "시간": now,
                "소음(dB)": db
            })

            if db < 45:

                st.success("🟢 매우 조용합니다.")

                st.session_state.quiet_count += 1

            elif db < 60:

                st.warning("🟡 약간 시끄럽습니다.")

                st.session_state.quiet_count = 0

            else:

                st.error("🔴 너무 시끄럽습니다!")

                st.session_state.quiet_count = 0

            # 약 50번 조용함 달성 시 칭찬
            if st.session_state.quiet_count >= 50:

                st.balloons()

                st.success(
                    "🎉 오랫동안 조용한 분위기를 유지했습니다! 훌륭합니다!"
                )

                st.session_state.quiet_count = 0

    except Exception as e:
        st.error(f"오류 발생: {e}")

# 기록 표시
if len(st.session_state.history) > 0:

    st.subheader("📈 소음 기록")

    df = pd.DataFrame(st.session_state.history)

    st.line_chart(df["소음(dB)"])

    st.dataframe(df, use_container_width=True)

# 기준 안내
st.divider()

st.subheader("📋 소음 기준")

st.markdown("""
### 🟢 조용함
45 dB 미만

### 🟡 주의
45 ~ 60 dB

### 🔴 시끄러움
60 dB 이상
""")
