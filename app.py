import streamlit as st
from supabase import create_client
import requests
import pandas as pd

# --- [1. 스타일 및 세련된 레이아웃 설정] ---
st.set_page_config(page_title="NSD PRO MASTER", layout="wide")

# 래빗스탁 스타일 커스텀 CSS (클릭 가능한 카드 버튼 디자인)
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    
    /* 버튼을 카드/배너처럼 보이게 만드는 스타일 */
    div.stButton > button {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 12px;
        padding: 40px 20px;
        width: 100%;
        height: 180px;
        transition: 0.2s;
        display: block;
    }
    div.stButton > button:hover {
        border-color: #58A6FF;
        background-color: #1C2128;
        transform: translateY(-5px);
    }
    /* 버튼 안의 텍스트 스타일 */
    div.stButton > button p {
        font-size: 20px !important;
        font-weight: bold !important;
        color: #58A6FF !important;
    }
    
    /* 상단 배너 제목 스타일 */
    .page-title { font-size: 28px; font-weight: bold; color: #FFFFFF; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# DB 및 텔레그램 설정
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
TOKEN = "8306599736:AAHwT_jhT9DHJqdWubOQoL1JuNlBbMjswGw"
CHAT_ID = "8182795005"

# --- [2. 페이지 이동 로직] ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'

def go_to(page_name):
    st.session_state.page = page_name
    st.rerun()

def load_watchlist():
    try:
        res = supabase.table('user_config').select('watchlist').eq('id', 1).execute()
        return res.data[0].get('watchlist', '') if res.data else ""
    except: return ""

# --- [3. 화면 렌더링] ---

# 현재 감시 종목 데이터 미리 로드
current_watchlist = load_watchlist()

# A. 메인 홈 화면 (4개 배너 그리드)
if st.session_state.page == 'home':
    st.markdown('<div class="page-title">🛡️ NSD PRO 마스터 터미널</div>', unsafe_allow_html=True)
    st.write("서비스를 선택하려면 아래 배너를 클릭하세요.")
    
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    
    with col1:
        if st.button("📡\nSEC 실시간 공시 센터"):
            go_to('sec')
    with col2:
        if st.button("⚠️\nREG SHO 분석 (준비중)"):
            go_to('regsho')
    with col3:
        if st.button("🔍\n종목 퀵 시세 검색 (준비중)"):
            go_to('search')
    with col4:
        if st.button("⚙️\n시스템 설정 및 테스트"):
            go_to('settings')

# B. SEC 실시간 공시 화면 (실제 작동)
elif st.session_state.page == 'sec':
    if st.button("⬅️ 메인 메뉴로 돌아가기"): go_to('home')
    st.title("📡 SEC 실시간 공시 센터")
    st.markdown("---")
    st.subheader("현재 실시간 감시 중인 종목")
    st.info(f"**{current_watchlist if current_watchlist else '없음'}**")
    st.write("파이썬애니웨어 엔진이 위 종목들을 20초마다 확인하며 새 공시 발견 시 텔레그램을 보냅니다.")

# C. 시스템 설정 및 테스트 (실제 작동)
elif st.session_state.page == 'settings':
    if st.button("⬅️ 메인 메뉴로 돌아가기"): go_to('home')
    st.title("⚙️ 시스템 설정 및 컨트롤")
    st.markdown("---")
    
    # 종목 수정 섹션
    st.subheader("🛠️ 감시 종목 업데이트")
    new_tickers = st.text_area("티커를 입력하세요 (쉼표 구분)", value=current_watchlist, height=100)
    if st.button("💾 설정 저장 (DB 동기화)"):
        supabase.table('user_config').upsert({"id": 1, "watchlist": new_tickers}).execute()
        st.success("✅ 성공적으로 저장되었습니다! 엔진이 새 목록을 즉시 감시합니다.")
        st.rerun()
        
    st.markdown("---")
    # 테스트 섹션
    st.subheader("🔔 연결 상태 테스트")
    if st.button("테스트 알림 발송"):
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": "🔔 조종석 연동 확인 성공!"})
        st.success("텔레그램 메시지를 확인하세요.")

# D. 나머지 준비중인 화면들
elif st.session_state.page in ['regsho', 'search']:
    if st.button("⬅️ 메인 메뉴로 돌아가기"): go_to('home')
    st.title("🚧 기능 준비 중")
    st.error(f"선택하신 '{st.session_state.page}' 기능은 현재 데이터 연동 작업 중입니다.")
