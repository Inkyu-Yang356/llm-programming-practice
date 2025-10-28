import streamlit as st
import openai
import os
from dotenv import load_dotenv
from datetime import datetime

# .env 파일 로드
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)

# 금지 키워드 로드
FORBIDDEN_KEYWORDS = os.getenv('FORBIDDEN_KEYWORDS', '').split(',')
FORBIDDEN_KEYWORDS = [keyword.strip() for keyword in FORBIDDEN_KEYWORDS if keyword.strip()]

# Streamlit 페이지 설정
st.set_page_config(
    page_title="보안 강화 챗봇 에이전트",
    page_icon="🛡️",
    layout="wide"
)

# CSS 스타일 추가 (어두운 테마)
st.markdown("""
<style>
    .main-title {
        text-align: center;
        font-size: 2.5rem;
        color: #4fc3f7;
        margin-bottom: 2rem;
    }
    .chat-container {
        background-color: #2e2e2e;
        border: 2px solid #404040;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .center-content {
        text-align: center;
    }
    .chat-subject {
        text-align: center;
        background-color: #1e3a1e;
        padding: 10px;
        border-radius: 10px;
        margin: 10px 0;
        border: 1px solid #2d5a2d;
        color: #a5d6a7;
    }
</style>
""", unsafe_allow_html=True)

# 메인 헤더 (가운데 정렬)
st.markdown('<h1 class="main-title">🛡️ 보안 강화 챗봇 에이전트</h1>', unsafe_allow_html=True)

# 사이드바 설정
with st.sidebar:
    st.header("⚙️ 에이전트 설정")
    
    # Temperature 설정
    temp_options = {
        "창의적 (높음)": 1.0,
        "균형 (보통)": 0.7,
        "보수적 (낮음)": 0.2
    }
    
    selected_temp = st.selectbox(
        "창의성 레벨",
        list(temp_options.keys()),
        index=1  # 기본값: 균형
    )
    
    temperature = temp_options[selected_temp]
    
    # 현재 Temperature 표시 (밝은 초록색)
    st.markdown(f"**현재 Temperature:** <span style='color: #32CD32; font-weight: bold;'>{temperature}</span>", unsafe_allow_html=True)
    
    st.divider()
    
    # 채팅 주제 표시 (가운데 정렬)
    st.markdown('<div class="chat-subject"><h4>💬 채팅 주제</h4><p>사이버보안 상담 및 교육</p></div>', unsafe_allow_html=True)

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 금지 키워드 확인 함수
def contains_forbidden_keywords(text):
    """사용자 입력에 금지 키워드가 포함되어 있는지 확인"""
    text_lower = text.lower()
    for keyword in FORBIDDEN_KEYWORDS:
        if keyword.lower() in text_lower:
            return True
    return False

# OpenAI API 호출 함수
def get_ai_response(user_input):
    try:
        # 시스템 메시지와 대화 히스토리 구성
        messages = [
            {"role": "system", "content": "당신은 친근하고 전문적인 사이버보안 상담가입니다. 사용자의 보안 관련 질문에 상담가의 따뜻한 어조로 답변해주세요."}
        ]
        
        # 최근 대화 히스토리 추가 (최대 10개)
        for msg in st.session_state.messages[-10:]:
            messages.append(msg)
            
        # 현재 사용자 입력 추가
        messages.append({"role": "user", "content": user_input})
        
        # OpenAI API 호출
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1000,
            temperature=temperature
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"오류가 발생했습니다: {str(e)}"

# 채팅 영역을 하이라이트로 감싸기
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# 첫 인사말 표시 (메시지가 없을 때만) - 가운데 정렬
if not st.session_state.messages:
    st.markdown('<div class="center-content">', unsafe_allow_html=True)
    st.chat_message("assistant").write("안녕하세요! 창의성 레벨을 조절하여 대화를 시작해보세요")
    st.markdown('</div>', unsafe_allow_html=True)

# 채팅 히스토리 표시 - 가운데 정렬
st.markdown('<div class="center-content">', unsafe_allow_html=True)
for message in st.session_state.messages:
    if message["role"] == "user":
        st.chat_message("user").write(message["content"])
    else:
        st.chat_message("assistant").write(message["content"])
st.markdown('</div>', unsafe_allow_html=True)

# 사용자 입력
if prompt := st.chat_input("보안 관련 질문을 입력하세요..."):
    # 사용자 메시지 표시
    st.chat_message("user").write(prompt)
    
    # 사용자 메시지를 세션 상태에 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 금지 키워드 확인
    if contains_forbidden_keywords(prompt):
        # 금지 키워드가 포함된 경우
        forbidden_response = "죄송합니다. 저는 금융 및 투자 상담을 할 수 없습니다."
        st.chat_message("assistant").write(forbidden_response)
        
        # 금지 응답을 세션 상태에 추가
        st.session_state.messages.append({"role": "assistant", "content": forbidden_response})
    else:
        # 정상적인 대화 진행
        with st.spinner("답변을 생성하고 있습니다..."):
            response = get_ai_response(prompt)
            
        st.chat_message("assistant").write(response)
        
        # AI 응답을 세션 상태에 추가
        st.session_state.messages.append({"role": "assistant", "content": response})

# 채팅 컨테이너 닫기
st.markdown('</div>', unsafe_allow_html=True)

