import streamlit as st
from supabase import create_client
import requests

# --- [1. 스타일 및 모바일 최적화 설정] ---
st.set_page_config(page_title="NSD PRO", layout="centered")

st.markdown("""
    <style>
    /* 전체 배경색 */
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    
    /* 배너 버튼: 모바일에서 높이를 70px로 대폭 축소 */
    div.stButton > button {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        height: 70px !important;
        width: 100%;
        margin-bottom: 10px;
        transition: 0.2s;
    }
    div.stButton > button:hover { border-color: #58A6FF; }
    div.stButton > button p { font-size: 14px !important; font-weight: bold !important; color: #58A6FF !important; }

    /* 뒤로가기 버튼: 아주 작고 심플하게 */
    .back-btn button {
        height: 30px !important;
        width: auto !important;
        font-size: 12px !important;
        padding: 0 10px !important;
        background-color: transparent !important;
        border: 1px solid #444 !important;
        color: #888 !important;
    }
    
    /* 상태창 박스 */
    .status-box {
        background-color: #1A1D23;
        padding: 12px;
        border-radius: 8px;
        border-left: 4px solid #00FFAA;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# DB 및 텔레그램 설정
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
TOKEN = "8306599736:AAHwT_jhT9DHJqdWubOQoL1JuNlBbMjswGw"
CHAT_ID = "8182795005"

# --- [2. 핵심 로직: SyntaxError 방지를 위해 명확히 분리] ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'

def go_to(page_name):
    st.session_state.page = page_name
    st.rerun()

def load_watchlist():
    try:
        res = supabase.table('user_config').select('watchlist').eq('id', 1).execute()
        if res.data:
            return res.data[0].get('watchlist', '')
        return ""
    except Exception:
        return ""

current_watchlist = load_watchlist()

# --- [3. 화면 렌더링] ---

# A. 메인 메뉴 (콤팩트한 4칸 그리드)
if st.session_state.page == 'home':
    st.markdown("<h4 style='text-align: center; color: #58A6FF; margin-bottom: 20px;'>🛡️ NSD PRO TERMINAL</h4>", unsafe_allow_html=True)
    
    # 2x2 그리드 배치
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📡 공시 센터"): go_to('sec')
        if st.button("🔍 시세 검색"): go_to('search')
    with c2:
        if st.button("⚠️ REG SHO"): go_to('regsho')
        if st.button("⚙️ 설정/테스트"): go_to('settings')
    
    st.markdown("---")
    st.caption(f"감시 중: {current_watchlist if current_watchlist else '없음'}")

# B. SEC 공시 센터 (감시 현황 + 설정 통합)
elif st.session_state.page == 'sec':
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("← 메뉴"): go_to('home')
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.subheader("📡 SEC 공시 센터")
    
    st.markdown(f'''<div class="status-box">
        <span style="color: #888; font-size: 11px;">현재 감시 종목</span><br>
        <span style="font-size: 16px; font-weight: bold; color: #00FFAA;">{current_watchlist if current_watchlist else '없음'}</span>
    </div>''', unsafe_allow_html=True)
    
    # 설정 기능을 공시 센터 하단에 배치
    with st.expander("🛠️ 감시 종목 변경하기", expanded=False):
        new_input = st.text_area("티커 입력 (쉼표 구분)", value=current_watchlist)
        if st.button("설정 저장"):
            try:
                supabase.table('user_config').upsert({"id": 1, "watchlist": new_input}).execute()
                st.success("완료!")
                st.rerun()
            except Exception as e:
                st.error("저장 실패")

    st.info("엔진이 20초 간격으로 신규 공시를 감시 중입니다.")

# C. 시스템 설정 (테스트 전용)
elif st.session_state.page == 'settings':
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("← 메뉴"): go_to('home')
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.subheader("⚙️ 시스템 설정")
    if st.button("🔔 텔레그램 테스트 알림"):
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": "🔔 조종석 테스트 성공!"})
        st.toast("발송 완료")

# D. 기타 준비중
else:
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("← 메뉴"): go_to('home')
    st.markdown('</div>', unsafe_allow_html=True)
    st.write(f"### {st.session_state.page.upper()} 기능 준비 중")
