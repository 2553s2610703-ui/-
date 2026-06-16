import streamlit as st
import numpy as np
import queue
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase

# 1. 페이지 기본 설정
st.set_page_config(page_title="실시간 교실 소음 신호등 🚦", page_icon="🚦", layout="centered")

st.title("🚦 실시간 교실 소음 신호등")
st.markdown("마이크 권한을 허용하면, 버튼을 누르지 않아도 **실시간으로 교실 소음을 측정**합니다.")

# 2. 사이드바 - 교실 활동 모드 설정
st.sidebar.header("⚙️ 교실 모드 설정")
classroom_mode = st.sidebar.selectbox(
    "현재 교실 활동을 선택하세요:",
    ["📝 시험 및 자습 (아주 조용히)", "👥 모둠 및 토론 활동 (적당히)", "🎨 자유 시간 (활기차게)"]
)

if "시험" in classroom_mode:
    threshold_warn, threshold_danger = 40, 60
    mode_desc = "목표 소음: 40 dB 이하 (매우 조용히)"
elif "모둠" in classroom_mode:
    threshold_warn, threshold_danger = 60, 75
    mode_desc = "목표 소음: 60 dB 이하 (적당한 대화)"
else:
    threshold_warn, threshold_danger = 75, 90
    mode_desc = "목표 소음: 75 dB 이하 (활기찬 상태)"

st.sidebar.info(mode_desc)

# 3. 오디오 처리를 위한 큐(Queue) 및 프로세서 정의
audio_queue = queue.Queue()

class NoiseProcessor(AudioProcessorBase):
    def recv_audio(self, frame):
        # 마이크로 들어온 디지털 오디오 신호를 수집
        sound_array = frame.to_ndarray()
        audio_queue.put(sound_array)
        return frame

# 4. 실시간 마이크 스트리밍 컴포넌트 (WebRTC)
ctx = webrtc_streamer(
    key="noise-signaling",
    mode=WebRtcMode.SENDONLY,  # 소리를 듣기만 하고 송출하진 않음
    audio_processor_factory=NoiseProcessor,
    media_stream_constraints={"video": False, "audio": True}, # 마이크만 사용
)

# 5. 소음 계산 및 화면 실시간 업데이트
if ctx.state.playing:
    # 실시간 데이터 표시를 위한 빈 공간(Placeholder) 생성
    status_box = st.empty()
    gauge_box = st.empty()
    msg_box = st.empty()

    while ctx.state.playing:
        try:
            # 큐에서 오디오 데이터 가져오기
            audio_data = audio_queue.get(timeout=1.0)
            
            # 음압(RMS) 기반 상대적 데시벨 계산
            if len(audio_data) > 0:
                rms = np.sqrt(np.mean(audio_data**2))
                # 사람이 느끼는 소리 크기(dB)와 유사하게 로그 스케일 변환
                db = int(20 * np.log10(rms + 1e-5) * 1.5) 
                db = max(20, min(db, 100)) # 20dB ~ 100dB 사이로 보정
            else:
                db = 20

            # 6. 실시간 UI 업데이트 (신호등 색상 변경)
            with status_box:
                st.markdown(f"## 🔊 현재 소음: **{db} dB**")
            
            with gauge_box:
                st.progress(db / 100)
            
            with msg_box:
                if db < threshold_warn:
                    st.success("🟢 **안전 (Good):** 교실이 아주 조용합니다. 최고예요!")
                elif db < threshold_danger:
                    st.warning("🟡 **주의 (Warning):** 조금씩 웅성거려요. 목소리를 낮춰주세요.")
                else:
                    st.error("🔴 **경고 (Danger):** 너무 시끄럽습니다! 정숙해 주세요!")

        except queue.Empty:
            # 데이터가 잠시 비어있을 때는 대기
            continue
else:
    st.info("▲ 위의 'Start' 버튼을 누르면 마이크가 켜지며 실시간 측정이 시작됩니다.")
