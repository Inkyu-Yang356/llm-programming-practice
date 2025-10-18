import streamlit as st

# 앱 제목
st.title("Streamlit 기본 구성요소 실습")

# 텍스트 입력
name = st.text_input("이름을 입력하세요:", placeholder="홍길동")
if name:
    st.write(f"안녕하세요, {name}님!")

# 버튼
if st.button("클릭하세요"):
    st.write("버튼이 클릭되었습니다!")

# 체크박스
if st.checkbox("체크박스 선택"):
    st.write("체크박스가 선택되었습니다!")

# 라디오 버튼
color = st.radio("좋아하는 색상을 선택하세요:", ["빨강", "파랑", "초록"])
st.write(f"선택한 색상: {color}")

# 셀렉트박스
hobby = st.selectbox("취미를 선택하세요:", ["독서", "운동", "게임", "여행"])
st.write(f"선택한 취미: {hobby}")

# 슬라이더
age = st.slider("나이를 선택하세요:", 0, 100, 25)  # 25 by default
st.write(f"선택한 나이: {age}")

# 멀티셀렉트
skills = st.multiselect("보유 기술을 선택하세요:", ["Python", "Java", "C++", "JavaScript"])
st.write(f"선택한 기술: {', '.join(skills)}")

# 파일 업로드
uploaded_file = st.file_uploader("파일을 업로드하세요:")
if uploaded_file:
    st.write(f"업로드된 파일 이름: {uploaded_file.name}")

# 컬럼 레이아웃
col1, col2 = st.columns(2)
with col1:
    st.write("왼쪽 컬럼")
    st.button("왼쪽 버튼")
with col2:
    st.write("오른쪽 컬럼")
    st.button("오른쪽 버튼")
    # hover effect
    st.markdown("""<style>
    div.stButton > button:hover {
    background-color: #4CAF50;
    color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# 진행률 표시
import time
st.write("진행률 표시:")
progress_bar = st.progress(0)

for i in range(101):
    time.sleep(0.01)
    progress_bar.progress(i)

# 코드 블록 표시
st.code("""
import streamlit as st

st.title("Hello, Streamlit!")
""", language="python")

# 완료 메시지
st.success("모든 구성요소를 실습했습니다!")  # Green message
st.warning("모든 구성요소를 실습했습니다!")  # Yellow message
st.error("모든 구성요소를 실습했습니다!")  # Red message