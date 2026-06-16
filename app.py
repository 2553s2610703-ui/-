import streamlit as st
import pandas as pd
import datetime

# 1. 페이지 설정
st.set_page_config(page_title="착한 소음 신호등 🚦", page_icon="🚦", layout="centered")

st.title("🚦 우리 반 착한 소음 신호등")
st.markdown("마이크 녹음 없이, 현재 교실의 소음 상태를 기록하고 모니터링하는 대시보드입니다.")

# 세션 상태(데이터 저장소) 초기화
if "noise_logs" not in st.session_state:
    st.session_state.noise_logs = []

# 2. 사이드바 - 활동 모드 설정
st.sidebar.header("⚙️ 수업 모드 설정")
classroom_mode = st.sidebar.selectbox(
    "현재 교실 활동:",
    ["📝 시험 및 자습 시간", "👥 모둠 및 토론 활동", "🎨 자유 및 쉬는 시간"]
)

if st.sidebar.button("📊 소음 기록 초기화"):
    st.session_state.noise_logs = []
    st.rerun()

# 3. 메인 - 현재 소음 상태 입력 (선생님 또는 소음 밭장이 클릭)
st.subheader("📢 현재 교실 소음 상태 선택")
st.caption("교실 상태에 맞는 버튼을 누르면 신호등과 그래프가 실시간으로 업데이트됩니다.")

col1, col2, col3 = st.columns(3)

current_status = None
score_value = 0

with col1:
    if st.button("🟢 아주 조용함", use_container_width=True):
        current_status = "Good"
        score_value = 20  # 소음 수치 (낮을수록 좋음)

with col2:
    if st.button("🟡 조금 웅성거림", use_container_width=True):
        current_status = "Warning"
        score_value = 55

with col3:
    if st.button("🔴 너무 시끄러움", use_container_width=True):
        current_status = "Danger"
        score_value = 90

# 버튼이 눌렸다면 데이터 저장
if current_status:
    now_time = datetime.datetime.now().strftime("%H:%M:%S")
    st.session_state.noise_logs.append({
        "시간": now_time, 
        "소음 상태": current_status, 
        "소음 수치(dB)": score_value
    })

# 4. 실시간 신호등 및 경고창 표시
st.markdown("---")
if st.session_state.noise_logs:
    latest_log = st.session_state.noise_logs[-1]
    status = latest_log["소음 상태"]
    
    if status == "Good":
        st.success("### 🟢 현재 상태: 안전 (아주 조용해요)\n지금처럼 자습 분위기를 잘 유지해 주세요! 최고입니다.")
    elif status == "Warning":
        st.warning("### 🟡 현재 상태: 주의 (조금 시끄러워요)\n목소리를 조금만 낮춰서 옆 친구에게만 들리게 말해요.")
    elif status == "Danger":
        st.error("### 🔴 현재 상태: 경고 (너무 시끄럽습니다)\n교실 전체가 너무 어수선합니다. 잠시 목소리를 멈춰주세요!")
else:
    st.info("💡 위의 버튼을 눌러 현재 교실의 소음 상태를 먼저 입력해 주세요.")

# 5. 소음 추이 그래프 및 통계
st.markdown("---")
st.subheader("📈 수업 시간 소음 기록 그래프")

if st.session_state.noise_logs:
    df = pd.DataFrame(st.session_state.noise_logs)
    
    # 라인 차트 시각화
    st.line_chart(df.set_index("시간")["소음 수치(dB)"])
    
    # 간단한 통계 요약
    stat_col1, stat_col2 = st.columns(2)
    with stat_col1:
        avg_score = int(df["소음 수치(dB)"].mean())
        st.metric("수업 평균 소음 수치", f"{avg_score} dB")
    with stat_col2:
        st.metric("기록 횟수", f"{len(df)} 회")
        
    # 데이터 표 보여주기
    with st.expander("📋 상세 기록 보기"):
        st.dataframe(df, use_container_width=True)
else:
    st.caption("입력된 소음 기록이 여기에 그래프로 표시됩니다.")
