import streamlit as st
import difflib
import time
import pandas as pd
from datetime import datetime

# 1. 페이지 및 스타일 설정
st.set_page_config(page_title="속기기능사 3급 연습기", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stTextArea textarea { font-size: 1.25rem !important; line-height: 1.7 !important; font-family: 'Pretendard', sans-serif; }
    .diff-added { color: #d93025; text-decoration: line-through; background-color: #fce8e6; } /* 오자/첨자 */
    .diff-removed { background-color: #fff475; font-weight: bold; border-bottom: 2px solid #f9ab00; } /* 탈자 */
    .metric-box { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 2. 핵심 로직 함수
def get_styled_diff(original, user_input):
    """원문과 입력문을 비교하여 HTML 형태로 반환"""
    result = []
    diff = difflib.ndiff(original, user_input)
    for char in diff:
        if char[0] == ' ': # 정답
            result.append(f"<span>{char[2:]}</span>")
        elif char[0] == '-': # 탈자 (원문에만 있음)
            result.append(f"<span class='diff-removed'>{char[2:]}</span>")
        elif char[0] == '+': # 오자/첨자 (사용자가 추가함)
            result.append(f"<span class='diff-added'>{char[2:]}</span>")
    return "".join(result)

def calculate_metrics(original, user_input, elapsed_time):
    """정확도 및 CPM(분당 타수) 계산"""
    matcher = difflib.SequenceMatcher(None, original, user_input)
    accuracy = matcher.ratio() * 100
    char_count = len(user_input)
    cpm = (char_count / (elapsed_time / 60)) if elapsed_time > 0 else 0
    return round(accuracy, 2), round(cpm, 0)

# 3. 세션 상태 관리
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'practice_active' not in st.session_state:
    st.session_state.practice_active = False

# 4. 사이드바 구성
with st.sidebar:
    st.header("⚙️ 연습 설정")
    st.selectbox("급수", ["속기기능사 3급"])
    mode = st.radio("텍스트 유형", ["논설체 (270자/분)", "연설체 (290자/분)"])
    st.divider()
    st.info("💡 팁: '연습 시작'을 누르면 5초 카운트다운 후 타이머가 작동합니다.")

# 5. 연습용 원문 데이터
target_script = """국민 여러분 안녕하십니까. 오늘 우리는 새로운 시대를 맞이하고 있습니다. 우리가 직면한 여러 가지 경제적 어려움을 극복하고 더 나은 미래를 만들기 위해서는 정부와 국민이 함께 힘을 모아야 할 때입니다. 특히 첨단 기술의 발전은 우리에게 새로운 기회를 제공하고 있으며 이를 잘 활용하는 것이 국가 경쟁력의 핵심이 될 것입니다. 끊임없는 도전과 혁신만이 우리 공동체의 번영을 보장할 수 있습니다."""

# 6. 메인 UI 레이아웃
st.title("⌨️ 속기기능사 실기 연습 플랫폼")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📖 연습 원문")
    st.text_area("연습 스크립트", target_script, height=200, disabled=True, label_visibility="collapsed")
    st.write("🎵 **오디오 가이드**")
    st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3") # 실제 파일 경로로 교체 가능

with col2:
    st.subheader("✍️ 실시간 입력창")
    user_input = st.text_area("여기에 타이핑하세요", height=250, placeholder="연습 시작 버튼을 누르세요...", label_visibility="collapsed")

st.divider()

# 7. 제어 버튼 및 카운트다운 로직
c1, c2, c3 = st.columns(3)

# [연습 시작 버튼]
if c1.button("🚀 연습 시작", use_container_width=True, variant="primary"):
    countdown_place = st.empty()
    for i in range(5, 0, -1):
        countdown_place.markdown(f"<h1 style='text-align:center; font-size:80px; color:#FF4B4B;'>{i}</h1>", unsafe_allow_html=True)
        time.sleep(1)
    countdown_place.markdown("<h1 style='text-align:center; font-size:80px; color:#28a745;'>START!</h1>", unsafe_allow_html=True)
    time.sleep(0.5)
    countdown_place.empty()
    
    st.session_state.start_time = time.time()
    st.session_state.practice_active = True
    st.rerun()

# [채점하기 버튼]
if c2.button("✅ 채점하기", use_container_width=True):
    if st.session_state.start_time:
        end_time = time.time()
        elapsed = end_time - st.session_state.start_time
        
        accuracy, cpm = calculate_metrics(target_script, user_input, elapsed)
        
        # 결과 대시보드
        res_col1, res_col2, res_col3 = st.columns(3)
        with res_col1:
            st.metric("정확도", f"{accuracy}%")
        with res_col2:
            st.metric("분당 타수(CPM)", f"{int(cpm)}자")
        with res_col3:
            st.metric("소 : 요 시간", f"{int(elapsed)}초")
            
        # 오답 리포트 시각화
        st.subheader("🔍 상세 오답 분석")
        diff_html = get_styled_diff(target_script, user_input)
        st.markdown(f"""
            <div style="background-color: white; padding: 25px; border-radius: 10px; border: 1px solid #dee2e6; line-height: 2.0; font-size: 1.1rem;">
                {diff_html}
            </div>
            <div style="margin-top: 15px; font-size: 0.9rem; color: #666;">
                <span style="background-color: #fff475; padding: 2px 5px;">노란색 배경</span> : 탈자(누락) | 
                <span style="color: #d93025; text-decoration: line-through;">빨간색 취소선</span> : 오자 및 첨자
            </div>
        """, unsafe_allow_html=True)
        
        if accuracy >= 90:
            st.balloons()
            st.success("🎉 축하합니다! 3급 합격 기준을 통과했습니다.")
    else:
        st.error("먼저 '연습 시작' 버튼을 눌러주세요!")

# [다시 하기 버튼]
if c3.button("🔄 다시 하기", use_container_width=True):
    st.session_state.start_time = None
    st.session_state.practice_active = False
    st.rerun()
