import streamlit as st
import numpy as np
import pandas as pd
import time
from audiorecorder import audiorecorder

# 1. 페이지 기본 설정 및 스타일
st.set_page_config(page_title="교실 소음 신호등 🚦", page_icon="🔇", layout="centered")

st.title("🚦 교실 소음 신호등 (Noise Monitor)")
st.markdown("""
학생들의 소음을 측정하고 관리하는 앱입니다. 
아래의 **'🎙️ 소음 측정 시작'** 버튼을 누르고 교실 소리를 녹음해보세요!
""")

# 세션 상태 초기화 (소음 기록 저장용)
if "noise_history" not in st.session_state:
    st.session_state.noise_history = []

# 2. 사이드바 - 교실 활동 모드 설정
st.sidebar.header("⚙️ 교실 모드 설정")
classroom_mode = st.sidebar.selectbox(
    "현재 교실 활동을 선택하세요:",
    ["📝 시험 및 자습 (아주 조용히)", "👥 모둠 및 토론 활동 (적당히)", "🎨 자유 시간 (활기차게)"]
)

# 모드별 기준치 설정 (임의의 상대적 데시벨 스케일)
if "시험" in classroom_mode:
    threshold_warn = 30
    threshold_danger = 50
    mode_desc = "현재는 아주 조용해야 하는 시간입니다. (목표: 30 이하)"
elif "모둠" in classroom_mode:
    threshold_warn = 55
    threshold_danger = 75
    mode_desc = "친구들과 대화하는 시간입니다. (목표: 55 이하)"
else:
    threshold_warn = 70
    threshold_danger = 90
    mode_desc = "자유롭게 소통하는 시간입니다. (목표: 70 이하)"

st.sidebar.info(mode_desc)

# 소음 기록 초기화 버튼
if st.sidebar.button("📊 소음 기록 초기화"):
    st.session_state.noise_history = []
    st.rerun()

# 3. 메인 기능 - 소음 녹음 및 분석
st.subheader("🎙️ 소음 측정하기")
st.caption("팁: 버튼을 한 번 눌러 녹음을 시작하고, 원하는 만큼 소음을 낸 뒤 다시 눌러 녹음을 종료하세요.")

# 오디오 레코더 컴포넌트 생성 (버튼 텍스트 커스텀)
audio = audiorecorder("▶️ 소음 측정 시작 (클릭)", "⏹️ 측정 완료 (다시 클릭)")

if len(audio) > 0:
    try:
        # 오디오 데이터를 numpy 배열로 변환
        wav_data = audio.frame_data
        audio_array = np.frombuffer(wav_data, dtype=np.int16)
        
        # 신호의 RMS(Root Mean Square)를 계산하여 소음 크기 수치화 (상대적 수치)
        if len(audio_array) > 0:
            rms = np.sqrt(np.mean(audio_array**2))
            
            # 사람이 이해하기 쉬운 0~100 스케일의 데시벨(상대값)로 변환
            # 로그 스케일을 적용하되 오류 방지를 위해 최소값 제한
            raw_db = 20 * np.log10(rms) if rms > 1 else 0
            calculated_db = min(int(max(raw_db - 20, 10)), 100) # 10~100 사이로 보정
        else:
            calculated_db = 10
            
    except Exception as e:
        st.error(f"오디오 분석 중 오류가 발생했습니다: {e}")
        calculated_db = 10

    # 현재 시간 기록
    current_time = time.strftime("%H:%M:%S")
    st.session_state.noise_history.append({"시간": current_time, "소음(dB)": calculated_db})

    # 4. 결과 시각화 (신호등 효과)
    st.markdown("---")
    st.markdown(f"### 📊 현재 교실 소음 결과: **{calculated_db} dB**")

    # 상태에 따른 대형 카드 및 메시지 출력
    if calculated_db < threshold_warn:
        st.success("🟢 **안전 (Good):** 교실이 아주 훌륭하게 통제되고 있습니다! 잘하고 있어요.")
        st.balloons()
    elif calculated_db < threshold_danger:
        st.warning("🟡 **주의 (Warning):** 조금씩 시끄러워지고 있습니다. 목소리를 조금만 낮춰주세요.")
    else:
        st.error("🔴 **경고 (Danger):** 교실이 너무 시끄럽습니다! 정숙해주세요.")
        
    st.progress(calculated_db / 100)

# 5. 소음 통계 및 그래프 분석
st.markdown("---")
st.subheader("📈 수업 시간 소음 변화 추이")

if st.session_state.noise_history:
    df = pd.DataFrame(st.session_state.noise_history)
    
    # 라인 차트 표시
    st.line_chart(df.set_index("시간"))
    
    # 통계 요약
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("최대 소음", f"{df['소음(dB)'].max()} dB")
    with col2:
        st.metric("평균 소음", f"{int(df['소음(dB)'].mean())} dB")
    with col3:
        st.metric("측정 횟수", f"{len(df)} 회")
else:
    st.info("아직 측정된 데이터가 없습니다. 상단의 버튼을 눌러 소음을 먼저 측정해주세요.")
