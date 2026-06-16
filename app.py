\import streamlit as st
import numpy as np
import pandas as pd
import time
import wave
import io
from streamlit_mic_recorder import mic_recorder

st.set_page_config(
    page_title="교실 소음 신호등",
    page_icon="🚦",
    layout="wide"
)

st.title("🚦 교실 소음 신호등")
st.write("녹음한 소리를 분석하여 교실 소음 수준을 표시합니다.")

# 세션 상태 초기화
if "history" not in st.session_state:
    st.session_state.history = []

if "quiet_count" not in st.session_state:
    st.session_state.quiet_count = 0

# 소음 계산 함수 (WAV 바이너리에서 순수 PCM 추출)
def calculate_noise(audio_bytes):
    try:
        # 바이너리 데이터를 파일처럼 읽기
        audio_file = io.BytesIO(audio_bytes)
        
        with wave.open(audio_file, 'rb') as wav:
            # WAV 파일의 순수 프레임 데이터 읽기
            raw_data = wav.readframes(wav.getnframes())
            # int16 형태로 변환
            audio_data = np.frombuffer(raw_data, dtype=np.int16)

        if len(audio_data) == 0:
            return 0

        # RMS 계산
        rms = np.sqrt(np.mean(audio_data.astype(np.float64) ** 2))

        if rms <= 0:
            return 0

        # 데시벨 계산 (마이크 및 환경에 따라 기준값 조정이 필요할 수 있습니다)
        db = 20 * np.log10(rms)

        return round(db, 1)

    except Exception as e:
        # 디버깅을 위해 에러 로그를 콘솔에 남기거나 0 반환
        return 0

st.subheader("🎤 소음 측정")

# mic_recorder는 기본적으로 wav 포맷으로 데이터를 제공합니다.
audio = mic_recorder(
    start_prompt="🎙️ 녹음 시작",
    stop_prompt="⏹️ 녹음 종료",
    format="wav", # 포맷을 명시적으로 지정
    key="noise"
)

if audio is not None:
    try:
        audio_bytes = audio.get("bytes")

        if audio_bytes:
            db = calculate_noise(audio_bytes)

            st.metric("현재 소음 수준", f"{db} dB")

            now = time.strftime("%H:%M:%S")

            # 기록 추가
            st.session_state.history.append({
                "시간": now,
                "소음(dB)": db
            })

            # 신호등 로직 변경 (데이터가 누적되므로 st.success 등이 새로고침되어도 유지되게 하려면 시각화 고려 필요)
            if db < 45:
                st.success("🟢 매우 조용합니다.")
                st.session_state.quiet_count += 1
            elif db < 60:
                st.warning("🟡 약간 시끄럽습니다.")
                st.session_state.quiet_count = 0
            else:
                st.error("🔴 너무 시끄럽습니다!")
                st.session_state.quiet_count = 0

            # 약 50번 조용함 달성 시 칭찬 (수동 녹음 방식이므로 테스트를 위해선 횟수를 낮추는 것을 추천)
            if st.session_state.quiet_count >= 50:
                st.balloons()
                st.success("🎉 오랫동안 조용한 분위기를 유지했습니다! 훌륭합니다!")
                st.session_state.quiet_count = 0

    except Exception as e:
        st.error(f"오류 발생: {e}")

# 기록 표시
if len(st.session_state.history) > 0:
    st.subheader("📈 소음 기록")
    
    df = pd.DataFrame(st.session_state.history)
    
    # X축을 '시간'으로 설정하여 라인 차트 시각화 개선
    st.line_chart(df.set_index("시간")["소음(dB)"])
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
