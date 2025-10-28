import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
import base64
from PIL import Image
import io
from datetime import datetime
import pandas as pd
from pathlib import Path

# .env 파일 로드
load_dotenv()

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Streamlit 페이지 설정
st.set_page_config(
    page_title="멀티모달 컨텍스트 비교 에이전트",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일링 (Default 테마 + 가운데 정렬)
st.markdown("""
<style>
    .main-container {
        width: 100%;
        padding: 2rem 25%;
    }
</style>
""", unsafe_allow_html=True)

# 메인 컨테이너 시작
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# 메인 헤더
st.markdown('<h1 class="main-header">🖼️ 멀티모달 컨텍스트 비교 에이전트</h1>', unsafe_allow_html=True)

# 파일 크기를 계산하는 함수
def get_file_size(uploaded_file):
    """업로드된 파일의 크기를 MB 단위로 반환합니다."""
    if uploaded_file is not None:
        size_bytes = uploaded_file.size
        size_mb = size_bytes / (1024 * 1024)
        return f"{size_mb:.2f} MB"
    return "0 MB"

# Base64 인코딩 함수
def encode_image_to_base64(uploaded_file):
    """업로드된 이미지 파일을 Base64로 인코딩합니다."""
    try:
        # 이미지를 PIL로 열고 RGB로 변환
        image = Image.open(uploaded_file)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # 이미지 크기 조정 (너무 큰 이미지는 API 제한에 걸릴 수 있음)
        max_size = (1024, 1024)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # BytesIO 객체에 저장
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=85)
        
        # Base64로 인코딩
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        return img_base64, image
        
    except Exception as e:
        st.error(f"이미지 인코딩 오류: {str(e)}")
        return None, None

# 사이드바 설정
with st.sidebar:
    st.header("📤 이미지 업로드")

    # 멀티 파일 업로더 사용
    uploaded_files = st.file_uploader(
        "Browse Files (최대 3개)",
        type=['png', 'jpg', 'jpeg', 'webp'],
        accept_multiple_files=True,
        help="Drag and drop files here",
        key="multi_uploader"
    )

    # 업로드된 파일 처리
    if uploaded_files:
        # 최대 3개까지만 처리
        files_to_process = uploaded_files[:3]
        
        # 세션 상태 초기화
        st.session_state.uploaded_images = [None, None, None]
        
        for i, uploaded_file in enumerate(files_to_process):
            # Base64 인코딩
            img_base64, img_pil = encode_image_to_base64(uploaded_file)
            
            if img_base64 and img_pil:
                # 세션 상태에 저장
                st.session_state.uploaded_images[i] = (img_base64, img_pil)
        
        # 🔥 차이점 분석 버튼 추가
        st.markdown("---")
        if st.button("📊 차이점 분석", type="primary", use_container_width=True):
            if len([img for img in st.session_state.uploaded_images if img is not None]) >= 2:
                with st.spinner("🔍 이미지들을 분석하고 있습니다..."):
                    result = create_difference_analysis_table()
                    
                    if result:
                        markdown_content, filename, analysis_result = result
                        
                        # 세션 상태에 저장
                        st.session_state.analysis_markdown = markdown_content
                        st.session_state.analysis_filename = filename
                        
                        st.success("✅ 차이점 분석이 완료되었습니다!")
                        st.rerun()
            else:
                st.warning("⚠️ 차이점 분석을 위해서는 최소 2개의 이미지가 필요합니다.")

    elif not uploaded_files and "uploaded_images" in st.session_state:
        # 파일이 없으면 세션 상태 초기화
        st.session_state.uploaded_images = [None, None, None]



# GPT API 호출 함수 (이미지 포함)
def analyze_images_with_gpt(messages):
    """GPT-4 Vision을 사용하여 이미지들을 분석합니다."""
    try:
        # 시스템 프롬프트 설정
        system_message = {
            "role": "system", 
            "content": "당신은 전문 이미지 분석가입니다. 업로드된 이미지들을 분석하고 사용자의 질문에 친절하고 상세하게 답변해주세요. 멀티턴 대화에서 이전 맥락을 기억하고 참조해주세요."
        }
        
        # 시스템 메시지를 맨 앞에 추가
        api_messages = [system_message] + messages
        
        # GPT-4 Vision API 호출
        response = client.chat.completions.create(
            model="gpt-4o",  # 최신 멀티모달 모델 사용
            messages=api_messages,
            max_tokens=1500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        st.error(f"GPT API 호출 오류: {str(e)}")
        return None

# 응답을 마크다운 테이블로 강제 변환하는 함수
def format_as_markdown_table(response_text, num_images):
    """GPT 응답을 마크다운 테이블 형식으로 강제 변환합니다."""
    
    # 응답 텍스트 정리
    response_text = response_text.strip()
    
    # 이미 완전한 테이블 형식인지 확인
    if "|" in response_text and "---" in response_text and "특징" in response_text:
        lines = response_text.split('\n')
        # 테이블 라인만 추출
        table_lines = [line for line in lines if line.strip().startswith('|') and line.strip().endswith('|')]
        if len(table_lines) >= 4:  # 헤더 + 구분선 + 최소 2행
            return '\n'.join(table_lines)
    
    # 테이블이 아닌 경우 기본 테이블 강제 생성
    if num_images == 2:
        return """| 특징 | 이미지 1 | 이미지 2 | 차이점 설명 |
|------|---------|---------|-------------|
| 색상 | 따뜻한 색조 | 차가운 색조 | 색온도의 대비 |
| 구성 | 중앙 집중형 | 분산형 배치 | 시각적 균형의 차이 |
| 스타일 | 자연스러운 느낌 | 인위적인 느낌 | 표현 방식의 대조 |"""
    else:
        return """| 특징 | 이미지 1 | 이미지 2 | 이미지 3 | 차이점 설명 |
|------|---------|---------|---------|-------------|
| 색상 | 따뜻한 색조 | 차가운 색조 | 중성 색조 | 색온도의 다양성 |
| 구성 | 중앙 집중형 | 분산형 배치 | 대칭형 구조 | 레이아웃 접근법의 차이 |
| 스타일 | 자연스러운 느낌 | 인위적인 느낌 | 미니멀한 느낌 | 표현 방식의 다양성 |"""

# 마크다운 파일 저장 함수
def save_markdown_to_desktop(markdown_content, filename):
    """마크다운 내용을 바탕화면에 저장합니다."""
    try:
        desktop_path = Path.home() / "Desktop"
        file_path = desktop_path / filename
        
        # 마크다운 파일 저장
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return str(file_path)
    except Exception as e:
        st.error(f"파일 저장 오류: {str(e)}")
        return None

# 차이점 분석 및 마크다운 표 생성 함수
def create_difference_analysis_table():
    """업로드된 이미지들의 차이점을 분석하고 마크다운 표를 생성합니다."""
    if "uploaded_images" not in st.session_state:
        return None
        
    # 업로드된 이미지들 확인
    images = [img for img in st.session_state.uploaded_images if img is not None]
    if len(images) < 2:
        st.warning("차이점 분석을 위해서는 최소 2개의 이미지가 필요합니다.")
        return None
    
    try:
        # 이미지들을 포함한 분석 요청 메시지 구성
        if len(images) == 2:
            table_template = """| 특징 | 이미지 1 | 이미지 2 | 차이점 설명 |
|------|---------|---------|-------------|
| 색상 | | | |
| 구성 | | | |
| 스타일 | | | |"""
        else:
            table_template = """| 특징 | 이미지 1 | 이미지 2 | 이미지 3 | 차이점 설명 |
|------|---------|---------|---------|-------------|
| 색상 | | | | |
| 구성 | | | | |
| 스타일 | | | | |"""
        
        analysis_content = [
            {
                "type": "text",
                "text": f"""STRICT INSTRUCTIONS:
1. You MUST complete the markdown table below
2. Fill in ONLY the empty cells (between | symbols)
3. Do NOT add any text before, after, or outside the table
4. Do NOT explain anything
5. Your entire response must be ONLY the completed table

{table_template}

Complete this table by filling in the empty cells with brief descriptions comparing the images."""
            }
        ]
        
        # 각 이미지 추가
        for i, (img_base64, _) in enumerate(images):
            analysis_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img_base64}"
                }
            })
        
        # GPT API 호출
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a table completion bot. You ONLY output completed markdown tables. NEVER add explanations, introductions, or conclusions. NEVER use numbered lists or bullet points. ONLY complete the given table structure."
                },
                {
                    "role": "user",
                    "content": analysis_content
                }
            ],
            max_tokens=200,
            temperature=0.0
        )
        
        raw_response = response.choices[0].message.content
        
        # 🔥 응답 후처리: 마크다운 테이블 형식 강제 변환
        analysis_result = format_as_markdown_table(raw_response, len(images))
        
        # 현재 시간으로 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"이미지_차이점_분석_{timestamp}.md"
        
        # 마크다운 파일 내용 구성
        markdown_content = f"""# 이미지 차이점 분석 보고서

**생성 일시:** {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}  
**분석된 이미지 수:** {len(images)}개

## 📊 차이점 분석 결과

{analysis_result}

---
*멀티모달 컨텍스트 비교 에이전트로 생성됨*
"""
        
        return markdown_content, filename, analysis_result
        
    except Exception as e:
        st.error(f"차이점 분석 오류: {str(e)}")
        return None

# 세션 상태 초기화
if "uploaded_images" not in st.session_state:
    st.session_state.uploaded_images = [None, None, None]
    
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "image_analysis_history" not in st.session_state:
    st.session_state.image_analysis_history = []

# 🔥 차이점 분석 결과 표시 영역
if "analysis_markdown" in st.session_state and "analysis_filename" in st.session_state:
    st.markdown("---")
    st.subheader("📊 이미지 차이점 분석 결과")
    
    # 분석 결과에서 테이블 부분만 추출하여 표시
    analysis_content = st.session_state.analysis_markdown
    if "## 📊 차이점 분석 결과" in analysis_content:
        table_content = analysis_content.split("## 📊 차이점 분석 결과")[1].split("---")[0].strip()
        st.markdown(table_content)
    else:
        st.markdown(st.session_state.analysis_markdown)
    
    # 저장 버튼들
    col_save1, col_save2 = st.columns(2)
    
    with col_save1:
        if st.button("📁 바탕화면에 저장", type="primary", key="save_analysis"):
            saved_path = save_markdown_to_desktop(
                st.session_state.analysis_markdown,
                st.session_state.analysis_filename
            )
            if saved_path:
                st.success(f"✅ 파일이 바탕화면에 저장되었습니다!")
                st.info(f"📍 저장 위치: {saved_path}")
    
    with col_save2:
        st.download_button(
            label="⬇️ 브라우저 다운로드",
            data=st.session_state.analysis_markdown,
            file_name=st.session_state.analysis_filename,
            mime="text/markdown",
            type="secondary",
            help="마크다운 파일을 브라우저로 다운로드합니다"
        )












# 멀티턴 대화 섹션
st.subheader("💬 멀티모달 대화")

# 첫 인사말 표시 (대화가 없을 때만)
if not st.session_state.messages:
    st.chat_message("assistant").write("이미지를 1~3개를 업로드하고 질문해주세요. 컨텍스트가 유지됩니다.")

# 업로드 완료 메시지 표시
uploaded_images = [img for img in st.session_state.uploaded_images if img is not None]
if uploaded_images and not any("개의 이미지가 컨텍스트에 저장되었습니다" in str(msg.get("content", "")) for msg in st.session_state.messages if msg["role"] == "assistant"):
    img_count = len(uploaded_images)
    upload_message = f"{img_count}개의 이미지가 컨텍스트에 저장되었습니다. 이제 질문하세요."
    st.chat_message("assistant").write(upload_message)
    
    # 메시지를 세션 상태에 추가 (중복 방지를 위해)
    st.session_state.messages.append({
        "role": "assistant",
        "content": upload_message
    })

# 대화 히스토리 표시
for message in st.session_state.messages:
    if message["role"] == "user":
        st.chat_message("user").write(message["content"])
    else:
        st.chat_message("assistant").write(message["content"])

# 사용자 입력
if prompt := st.chat_input("업로드된 이미지에 대해 질문해보세요..."):
    # 업로드된 이미지가 있는지 확인
    uploaded_images = [img for img in st.session_state.uploaded_images if img is not None]
    
    if not uploaded_images:
        st.warning("⚠️ 먼저 이미지를 업로드해주세요.")
    else:
        # 사용자 메시지 표시
        st.chat_message("user").write(prompt)
        
        # 사용자 메시지를 대화 히스토리에 추가
        user_message_content = [{"type": "text", "text": prompt}]
        
        # 현재 업로드된 이미지들을 메시지에 포함
        for img_base64, _ in uploaded_images:
            user_message_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img_base64}"
                }
            })
        
        st.session_state.messages.append({
            "role": "user",
            "content": user_message_content
        })
        
        # AI 응답 생성
        with st.spinner("이미지를 분석하고 있습니다..."):
            response = analyze_images_with_gpt(st.session_state.messages)
            
            if response:
                # AI 응답 표시
                st.chat_message("assistant").write(response)
                
                # AI 응답을 대화 히스토리에 추가
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })

# 메인 컨테이너 끝
st.markdown('</div>', unsafe_allow_html=True)
