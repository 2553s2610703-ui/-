import streamlit as st
from google import genai
from google.genai import types

# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="연애상담 챗봇",
    page_icon="💝",
    layout="centered"
)

st.title("💝 연애상담 챗봇")
st.caption("연애 고민을 편하게 이야기해 보세요.")

# -----------------------------
# API 키 로드
# -----------------------------
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("GEMINI_API_KEY가 Secrets에 설정되지 않았습니다.")
    st.stop()

# -----------------------------
# Gemini 클라이언트 생성
# -----------------------------
try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Gemini 클라이언트 생성 실패: {e}")
    st.stop()

# -----------------------------
# 시스템 프롬프트
# -----------------------------
SYSTEM_PROMPT = """
당신은 따뜻하고 공감 능력이 뛰어난 연애상담 전문가입니다.

규칙:
1. 사용자의 감정을 먼저 공감한다.
2. 섣부른 단정이나 비난을 하지 않는다.
3. 현실적이고 건강한 관계를 우선으로 조언한다.
4. 대화를 통해 상황을 충분히 파악하려고 한다.
5. 답변은 자연스러운 한국어로 작성한다.
6. 너무 길지 않게 답변하되 필요한 경우 구체적인 예시를 제공한다.
"""

# -----------------------------
# 채팅 기록 초기화
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# 기존 대화 출력
# -----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------------
# 사용자 입력
# -----------------------------
user_input = st.chat_input("연애 고민을 입력하세요")

if user_input:

    # 사용자 메시지 저장
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    # 사용자 메시지 출력
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):

        try:
            with st.spinner("생각 중..."):

                # 대화 이력 구성
                history_text = ""

                for msg in st.session_state.messages:
                    role = "사용자" if msg["role"] == "user" else "상담사"
                    history_text += f"{role}: {msg['content']}\n"

                prompt = f"""
{SYSTEM_PROMPT}

다음은 지금까지의 대화입니다.

{history_text}

상담사 답변:
"""

                response = client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.8,
                        max_output_tokens=1000
                    )
                )

                answer = response.text

                st.markdown(answer)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )

        except Exception as e:
            error_msg = (
                "죄송합니다. 응답 생성 중 오류가 발생했습니다.\n\n"
                f"오류 내용: {e}"
            )

            st.error(error_msg)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_msg
                }
            )

# -----------------------------
# 대화 초기화 버튼
# -----------------------------
st.divider()

if st.button("대화 초기화"):
    st.session_state.messages = []
    st.rerun()
