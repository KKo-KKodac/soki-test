import streamlit as st
import difflib
import time
import pandas as pd
import os

# 1. 페이지 설정 및 테마
st.set_page_config(page_title="속기기능사 연습기", layout="wide")

st.markdown("""
    <style>
    .stTextArea textarea { font-size: 1.2rem !important; line-height: 1.6 !important; }
    .diff-added { color: #d93025; text-decoration: line-through; background-color: #fce8e6; }
    .diff-removed { background-color: #fff475; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. 초기 세션 상태 설정 (에러 방지의 핵심)
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'user_text' not in st.session_state:
    st.session_state.user_text = ""
if 'is_counting' not in st.session_state:
    st.session_state.is_counting = False

# 3. 함수 정의
def get_styled_diff(original, user_input):
    result = []
    diff = difflib.ndiff(original, user_input)
    for char in diff:
        if char[0] == ' ':
            result.append(f"<span>{char[2:]}</span>")
        elif char[0] == '-': # 탈자
            result.append(f"<span class='diff-removed'>{char[2:]}</span>")
        elif char[0] == '+': # 오자
            result.append(f"<span class='diff-added'>{char[2:]}</span>")
    return "".join(result)

def calculate_metrics(original, user_input, start_time):
    if start_time is None:
        return 0.0, 0
    elapsed_time = time.time() - start_time
    matcher = difflib.SequenceMatcher(None, original, user_input)
    accuracy = matcher.ratio() * 100
    cpm = (len(user_input) / (elapsed_time / 60)) if elapsed_time > 0.5 else 0
    return round(accuracy, 2), round(cpm, 0), round(elapsed_time, 1)

# 4. 연습 데이터
target_script = """국민 여러분 안녕하십니까. 오늘 우리는 새로운 시대를 맞이하고 있습니다. 우리가 직면한 여러 가지 경제적 어려움을 극복하고 더 나은 미래를 만들기 위해서는 정부와 국민이 함께 힘을 모아야 할 때입니다. 특히 첨단 기술의 발전은 우리에게 새로운 기회를 제공하고 있으며 이를 잘 활용하는 것이 국가 경쟁력의 핵심이 될 것입니다."""

# 5. 메인 UI
st.title("⌨️ 속기기능사 3급 연습 플랫폼")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📖 연습 원문")
    st.info(target_script)
    st.write("🎵 **오디오 가이드**")
    st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")

with col2:
    st.subheader("✍️ 실시간 입력창")
    # 키보드 입력값을 세션 상태에 저장하여 유지
    user_input = st.text_area(
        "타이핑 영역", 
        value=st.session_state.user_text,
        height=250, 
        placeholder="연습 시작 버튼을 누르면 카운트다운 후 시작됩니다.",
        key="main_input",
        on_change=lambda: st.session_state.update(user_text=st.session_state.main_input)
    )

st.divider()

# 6. 제어 버튼
c1, c2, c3 = st.columns(3)

# [연습 시작]
if c1.button("🚀 연습 시작", use_container_width=True):
    st.session_state.user_text = "" # 텍스트 초기화
    countdown_place = st.empty()
    for i in range(5, 0, -1):
        countdown_place.markdown(f"<h1 style='text-align:center; color:#FF4B4B;'>{i}</h1>", unsafe_allow_html=True)
        time.sleep(1)
    countdown_place.markdown("<h1 style='text-align:center; color:#28a745;'>START!</h1>", unsafe_allow_html=True)
    time.sleep(0.5)
    countdown_place.empty()
    
    st.session_state.start_time = time.time()
    st.rerun()

# [채점하기]
if c2.button("✅ 채점하기", use_container_width=True):
    if st.session_state.start_time is not None:
        accuracy, cpm, elapsed = calculate_metrics(target_script, st.session_state.user_text, st.session_state.start_time)
        
        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.metric("정확도", f"{accuracy}%")
        m2.metric("타수 (CPM)", f"{cpm}자")
        m3.metric("시간", f"{elapsed}초")
        
        st.subheader("🔍 오답 분석 결과")
        diff_html = get_styled_diff(target_script, st.session_state.user_text)
        st.markdown(f"""
            <div style="background-color: white; padding: 20px; border: 1px solid #ddd; border-radius: 10px; line-height: 1.8;">
                {diff_html}
            </div>
        """, unsafe_allow_html=True)
        
        if accuracy >= 90:
            st.balloons()
    else:
        st.warning("먼저 '연습 시작' 버튼을 눌러주세요.")

# [다시 하기]
if c3.button("🔄 다시 하기", use_container_width=True):
    st.session_state.start_time = None
    st.session_state.user_text = ""
    st.rerun()
