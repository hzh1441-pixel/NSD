import streamlit as st
from supabase import create_client
import requests
import pandas as pd

# --- [1. 스타일 및 기본 설정] ---
# 앱 느낌을 위해 wide 모드 사용, 한국어 타이틀
st.set_page_config(page_title="NSD PRO 마스터 터미널", layout="wide") 

# 커스텀 CSS: 정사각형 칸(Card) 스타일 및 호버 효과
st.markdown("""
    <style>
    div.stButton > button {
        background-color: #1E1E1E;
        color: white;
        border: 2px solid #333;
        border-radius: 15px;
        height: 250px; /* 정사각형 느낌을 위한 높이 설정 */
        width: 100%;
        font-size: 20px;
        font-weight: bold;
        transition: 0.3s;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    div.stButton > button:hover {
        border-color: #00FFAA;
        color: #00FFAA;
        transform: scale(1.03);
        background-color: #1A1A1A;
    }
    .banner-sub-text {
        font-size: 14px;
        color: #888;
        font-weight: normal;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# DB 및 텔레그램 설정 (기존 데이터 유지)
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
TOKEN = "8306599736:AAHwT_jhT9DHJqdWubOQoL1JuNlBbMjswGw"
CHAT_ID = "8182795005"

# --- [2. 페이지 상태 관리] ---
if 'page' not in st.session_state:
    st.session_state.page = 'home' # 초기 화면

def go_to(page_name):
    st.session_state.page = page_name
    st.rerun()

# --- [3. 메인 화면: 2x2 그리드 배너] ---
if st.session_state.page == 'home':
    st.title("🛡️ NSD PRO 마스터 터미널")
    st.write("원하시는 서비스를 선택하세요.")
    st.divider()

    # 가로 2칸 열 만들기
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)

    # 1행 1열: SEC 공시 감시 (기능 작동 중)
    with row1_col1:
        if st.button("📡\nSEC 실시간 공시 센터\n<div class='banner-sub-text'>20초마다 새로운 공시 자동 감시 중</div>", use_container_width=True):
            go_to('sec')

    # 1행 2열: REG SHO 분석 (껍데기)
    with row1_col2:
        if st.button("⚠️\nREG SHO 분석 타임라인\n<div class='banner-sub-text'>연속 등재 일수 계산기 (업데이트 예정)</div>", use_container_width=True):
            go_to('regsho')

    # 2행 1열: 주가 검색 (껍데기)
    with row2_col1:
        if st.button("🔍\n종목 퀵 시세 검색\n<div class='banner-sub-text'>실시간 차트 및 FTD 데이터 (업데이트 예정)</div>", use_container_width=True):
            go_to('search')

    # 2행 2열: 시스템 설정 (기능 작동 중)
    with row2_col2:
        if st.button("⚙️\n시스템 컨트롤 센터\n<div class='banner-sub-text'>감시 종목 수정 및 텔레그램 테스트</div>", use_container_width=True):
            go_to('settings')

# --- [4. 상세 상세 화면 정의 (한국어)] ---

# A. SEC 감시 화면
elif st.session_state.page == 'sec':
    if st.button("⬅️ 메인 메뉴로 돌아가기"): go_to('home')
    st.header("📡 SEC 실시간 공시 감시 센터")
    res = supabase.table('user_config').select('watchlist').eq('id', 1).execute()
    watchlist = res.data[0].get('watchlist', '')
    st.success(f"현재 감시 중인 종목 리스트: **{watchlist}**")
    st.info("파이썬애니웨어 엔진이 뒤에서 24시간 내내 이 종목들을 감시하고 있습니다.")

# B. REG SHO 화면 (업데이트 예정)
elif st.session_state.page == 'regsho':
    if st.button("⬅️ 메인 메뉴로 돌아가기"): go_to('home')
    st.header("⚠️ REG SHO Threshold List 분석")
    st.warning("나스닥 공식 데이터를 분석하여 연속 등재 일수를 계산하는 기능은 아직 추가되지 않았습니다.")

# C. 주가 검색 화면 (업데이트 예정)
elif st.session_state.page == 'search':
    if st.button("⬅️ 메인 메뉴로 돌아가기"): go_to('home')
    st.header("🔍 종목 퀵 시세 검색")
    st.warning("실시간 주가 차트 및 FTD 데이터를 불러오는 기능은 아직 추가되지 않았습니다.")

# D. 설정 화면 (작동 중)
elif st.session_state.page == 'settings':
    if st.button("⬅️ 메인 메뉴로 돌아가기"): go_to('home')
    st.header("⚙️ 시스템 컨트롤 센터")
    st.divider()
    
    # 데이터 로딩
    res = supabase.table('user_config').select('watchlist').eq('id', 1).execute()
    current_val = res.data[0].get('watchlist', '')
    
    # 배너 형식으로 꾸미기
    st.subheader("🛠️ 감시 종목 리스트 수정")
    st.write("티커를 쉼표(,)로 구분해서 입력하세요 (예: BNAI, EMPD)")
    new_input = st.text_area("입력 칸", value=current_val, label_visibility="collapsed")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 설정 저장 및 엔진 동기화", use_container_width=True):
            supabase.table('user_config').upsert({"id": 1, "watchlist": new_input}).execute()
            st.success("성공적으로 저장되었습니다! 엔진이 즉시 새 목록을 읽어옵니다.")
            st.rerun()
    
    st.divider()
    st.subheader("🔔 텔레그램 연결 상태 테스트")
    if st.button("테스트 알림 보내기", use_container_width=True):
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": "🔔 NSD PRO 연결 확인 성공!"})
