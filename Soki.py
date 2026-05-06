import streamlit as st
import difflib
import time
import pandas as pd
from datetime import datetime

# --- 페이지 설정 ---
st.set_page_config(page_title="속기기능사 3급 연습기", layout="wide")

# --- 스타일 설정 ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stTextArea textarea { font-size: 1.2rem !important; line-height: 1.6 !important; }
    .diff-added { color: red; text-decoration: line-through; }
    .diff-removed { background-color: #ffeb3b; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 핵심 로직 함수 ---
def get_styled_diff(original, user_input):
    """원문과 입력문을 비교하여 HTML 형태로 반환"""
    result = []
    diff = difflib.ndiff(original, user_input)
    for char in diff:
        if char[0] == ' ': # 일치
            result.append(f"<span>{char[2:]}</span>")
        elif char[0] == '-': # 탈자 (원문에만 있음)
            result.append(f"<span class='diff-removed'>{char[2:]}</span>")
        elif char[0] == '+': # 오자/첨자 (사용자가 추가함)
            result.append(f"<span class='diff-added'>{char[2:]}</span>")
    return "".join(result)

def calculate_metrics(original, user_input, elapsed_time):
    """정확도 및 CPM 계산"""
    matcher = difflib.SequenceMatcher(None, original, user_input)
    accuracy = matcher.ratio() * 100
    
    # 분당 타수 계산 (글자 수 / 분)
    char_count = len(user_input)
    cpm = (char_count / (elapsed_time / 60)) if elapsed_time > 0 else 0
    return round(accuracy, 2), round(cpm, 0)

# --- 세션 상태 초기화 ---
if 'start_time' not in st.session_state:
    st.session_state.start_time = None

# --- 사이드바 (설정 및 기록) ---
with st.sidebar:
    st.header("⚙️ 연습 설정")
    level = st.selectbox("급수 선택", ["3급 (270~290자)"])
    mode = st.radio("모드 선택", ["논설체", "연설체"])
    
    st.divider()
    st.subheader("📊 최근 기록")
    # 예시 기록 데이터 (나중에 CSV 연결 가능)
    try:
        history = pd.read_csv("data/records.csv")
        st.dataframe(history.tail(5))
    except:
        st.write("아직 기록이 없습니다.")

# --- 메인 화면 UI ---
st.title("⌨️ 속기기능사 3급 실기 연습")
st.info(f"목표: {mode} 기준 정확도 90% 이상 달성")

# 연습용 샘플 데이터 (실제 운영 시에는 파일에서 로드하도록 변경 가능)
target_script = """국민 여러분 안녕하십니까. 오늘 우리는 새로운 시대를 맞이하고 있습니다. 
우리가 직면한 여러 가지 경제적 어려움을 극복하고 더 나은 미래를 만들기 위해서는 
정부와 국민이 함께 힘을 모아야 할 때입니다. 특히 첨단 기술의 발전은 우리에게 
새로운 기회를 제공하고 있으며 이를 잘 활용하는 것이 국가 경쟁력의 핵심이 될 것입니다."""

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📖 연습 원문")
    st.text_area("원문 보기", target_script, height=200, disabled=True)
    
    # 음원 컨트롤 (파일이 없을 경우 대비해 안내 메시지)
    st.write("🎵 오디오 컨트롤")
    st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3") # 예시 링크

with col2:
    st.subheader("✍️ 입력창")
    user_input = st.text_area("연습을 시작하면 이곳에 타이핑하세요.", height=250, placeholder="준비가 되면 입력을 시작하세요.")

# --- 제어 버튼 ---
c1, c2, c3 = st.columns(3)

if c1.button("🚀 연습 시작", use_container_width=True):
    st.session_state.start_time = time.time()
    st.success("연습이 시작되었습니다! 타이핑 후 '채점하기'를 눌러주세요.")

if c2.button("✅ 채점하기", use_container_width=True):
    if st.session_state.start_time:
        end_time = time.time()
        elapsed = end_time - st.session_state.start_time
        
        accuracy, cpm = calculate_metrics(target_script, user_input, elapsed)
        
        # 결과 표시
        st.divider()
        res_col1, res_col2, res_col3 = st.columns(3)
        res_col1.metric("정확도", f"{accuracy}%")
        res_col2.metric("분당 타수(CPM)", f"{cpm}자")
        res_col3.metric("소요 시간", f"{int(elapsed)}초")
        
        if accuracy >= 90:
            st.balloons()
            st.success("합격권입니다! 고생하셨습니다.")
        else:
            st.warning("정확도가 조금 아쉽습니다. 오답을 확인해보세요.")
            
        # 오답 분석
        st.subheader("🔍 오답 분석 리포트")
        diff_html = get_styled_diff(target_script, user_input)
        st.markdown(f"""
            <div style="background-color: white; padding: 20px; border-radius: 10px; border: 1px solid #ddd; line-height: 1.8;">
                {diff_html}
            </div>
            <p style='margin-top:10px; font-size: 0.9rem;'>
                💡 <span style='background-color: #ffeb3b;'>노란색</span>: 탈자(빠짐) | 
                <span style='color: red; text-decoration: line-through;'>빨간색</span>: 오자/첨자
            </p>
        """, unsafe_allow_html=True)
    else:
        st.error("먼저 '연습 시작' 버튼을 눌러주세요!")

if c3.button("🔄 다시 하기", use_container_width=True):
    st.session_state.start_time = None
    st.rerun()