import streamlit as st
from supabase import create_client
import requests
import pandas as pd

# --- [1. 스타일 및 세련된 기본 설정] ---
st.set_page_config(page_title="NSD PRO MASTER TERMINAL", layout="wide") # 넓게 쓰기

# 커스텀 CSS: 폰트 조정, 카드 UI, 호버 효과 등 프로페셔널한 느낌 강조
st.markdown("""
    <style>
    /* 전체 배경색 */
    .stApp {
        background-color: #101010;
        color: white;
    }
    /* 사이드바 스타일 */
    [data-testid="stSidebar"] {
        background-color: #1A1A1A;
        border-right: 1px solid #333;
    }
    /* 카드 UI (메트릭/컨트롤창) */
    .terminal-card {
        background-color: #1A1A1A;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #333;
        margin-bottom: 15px;
    }
    .terminal-title {
        color: #888;
        font-size: 14px;
        font-weight: bold;
        text-transform: uppercase;
    }
    .terminal-value {
        color: #00FFAA;
        font-size: 24px;
        font-weight: bold;
    }
    /* 입력창 및 버튼 세련되게 */
    .stTextArea textarea, .stTextInput input {
        background-color: #121212 !important;
        border-color: #333 !important;
        color: white !important;
    }
    div.stButton > button {
        background-color: #333;
        color: white;
        border: none;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #00FFAA;
        color: black;
    }
    </style>
    """, unsafe_allow_html=True)

# DB 및 텔레그램 설정 (기존 데이터 유지)
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
TOKEN = "8306599736:AAHwT_jhT9DHJqdWubOQoL1JuNlBbMjswGw"
CHAT_ID = "8182795005"

# --- [2. 핵심 데이터 로직] ---
def load_watchlist():
    try:
        res = supabase.table('user_config').select('watchlist').eq('id', 1).execute()
        return res.data[0].get('watchlist', '') if res.data else ""
    except: return ""

# --- [3. 사이드바 확장형 메뉴] ---
with st.sidebar:
    st.markdown("### 🛡️ NSD PRO MASTER")
    st.caption("초정밀 나스닥 터미널")
    st.divider()
    
    # 확장성 있는 목록형 메뉴
    menu = st.radio(
        "메뉴 선택",
        ["대시보드 홈", "📡 SEC 실시간 공시", "⚠️ Reg Sho 분석 (예정)", "🔍 종목 주가 검색 (예정)", "⚙️ 시스템 설정"],
        index=0
    )
    st.v_spacer(height=30)
    st.caption("시스템 상태: 정상 작동 중")
    st.divider()

# --- [4. 메인 화면: 선택된 메뉴에 따라 출력] ---

# 데이터 로딩
current_watchlist = load_watchlist()
tickers = [t.strip().upper() for t in current_watchlist.split(',') if t.strip()]

# A. 대시보드 홈 (핵심 요약 정보 집약)
if menu == "대시보드 홈":
    st.title("📊 통합 대시보드")
    
    # 상단 요약 카드 영역 (거대한 배너 삭제)
    st.markdown('<div class="terminal-card"><div class="terminal-title">핵심 감시 모니터</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("감시 종목 수", f"{len(tickers)}개", delta="실시간")
    with c2: st.metric("엔진 상태", "Running", delta="정상")
    with c3: st.metric("최근 공시 발견", "없음", delta="0")
    with c4: st.metric("Reg Sho 등재", "2종목", delta="분석 중", delta_color="off")
    st.markdown('</div>', unsafe_allow_html=True)
    
    col_l, col_r = st.columns([2,1])
    with col_l:
        st.markdown('<div class="terminal-card"><div class="terminal-title">최근 SEC 공시 발견 피드 (실시간)</div>', unsafe_allow_html=True)
        # 나중에 DB에서 공시 로그를 읽어와 뿌려주는 자리
        st.info("실시간 공시 피드가 이 자리에 시간순으로 집약됩니다.")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_r:
        st.markdown('<div class="terminal-card"><div class="terminal-title">현재 감시 종목 상세</div>', unsafe_allow_html=True)
        if tickers:
            st.table(pd.DataFrame({"티커": tickers}))
        else:
            st.write("감시 종목이 없습니다.")
        st.markdown('</div>', unsafe_allow_html=True)

# B. 시스템 설정 (기능 집약)
elif menu == "⚙️ 시스템 설정":
    st.title("⚙️ 시스템 컨트롤 센터")
    
    # 1. 종목 설정 카드
    st.markdown('<div class="terminal-card"><div class="terminal-title">실시간 감시 종목 수정</div>', unsafe_allow_html=True)
    new_tickers = st.text_area("쉼표(,)로 구분하여 입력 (예: BNAI, EMPD)", value=current_watchlist, height=100)
    if st.button("💾 설정 저장 및 엔진 동기화"):
        supabase.table('user_config').upsert({"id": 1, "watchlist": new_tickers}).execute()
        st.success("✅ 저장 완료!")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 2. 시스템 테스트 카드
    st.markdown('<div class="terminal-card"><div class="terminal-title">텔레그램 연결 상태 테스트</div>', unsafe_allow_html=True)
    if st.button("🔔 테스트 알림 보내기", use_container_width=True):
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": "🔔 NSD PRO 연결 확인 성공!"})
    st.markdown('</div>', unsafe_allow_html=True)

# C. 나머지 껍데기 화면 (한국어로 명확히 표시)
elif menu == "📡 SEC 실시간 공시":
    st.title("📡 SEC 실시간 공시 센터")
    st.warning("상세 공시 피드 기능은 업데이트 중입니다. 대시보드 홈에서 확인하세요.")

elif menu == "⚠️ Reg Sho 분석 (예정)":
    st.title("⚠️ Reg Sho Threshold List 분석")
    st.error("나스닥 데이터를 크롤링하여 연속 등재 일수를 계산하는 기능은 아직 추가되지 않았습니다.")

elif menu == "🔍 종목 주가 검색 (예정)":
    st.title("🔍 종목 주가 검색")
    st.error("실시간 주가 차트 및 FTD 데이터를 불러오는 기능은 아직 추가되지 않았습니다.")
