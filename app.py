import streamlit as st
from supabase import create_client
import requests
import pandas as pd

# --- [1. 기본 설정 및 디자인] ---
st.set_page_config(page_title="NSD PRO PORTAL", layout="centered") # 앱 느낌을 위해 가운데 정렬

# 배너 스타일링 CSS
st.markdown("""
    <style>
    .main-banner {
        background: linear-gradient(90deg, #121212 0%, #1e1e1e 100%);
        padding: 40px;
        border-radius: 15px;
        border: 1px solid #333;
        margin-bottom: 15px;
        cursor: pointer;
        transition: 0.3s;
        text-align: center;
    }
    .main-banner:hover {
        border-color: #00FFAA;
        transform: scale(1.02);
    }
    .banner-text {
        color: #00FFAA;
        font-size: 24px;
        font-weight: bold;
    }
    .sub-text {
        color: #888;
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

# DB 및 텔레그램 설정 (기존 데이터 유지)
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
TOKEN = "8306599736:AAHwT_jhT9DHJqdWubOQoL1JuNlBbMjswGw"
CHAT_ID = "8182795005"

# --- [2. 페이지 관리 로직] ---
if 'page' not in st.session_state:
    st.session_state.page = 'home' # 기본값은 홈 화면

def go_to(page_name):
    st.session_state.page = page_name
    st.rerun()

# --- [3. 각 화면 정의] ---

# A. 홈 화면 (배너 나열)
if st.session_state.page == 'home':
    st.title("🛡️ NSD PRO MASTER")
    st.write("진입하고 싶은 서비스를 선택하세요.")
    
    # 배너 1: SEC 공시
    if st.button("📡 [BANNER 01] SEC REAL-TIME FILINGS", use_container_width=True):
        go_to('sec')
    
    # 배너 2: REG SHO
    if st.button("⚠️ [BANNER 02] REG SHO THRESHOLD LIST", use_container_width=True):
        go_to('regsho')
        
    # 배너 3: 주가 검색
    if st.button("🔍 [BANNER 03] TICKER QUICK SEARCH", use_container_width=True):
        go_to('search')
        
    # 배너 4: 설정
    if st.button("⚙️ [BANNER 04] SYSTEM SETTINGS", use_container_width=True):
        go_to('settings')

# B. SEC 감시 화면
elif st.session_state.page == 'sec':
    if st.button("⬅️ BACK TO MENU"): go_to('home')
    st.header("📡 SEC 실시간 감시 센터")
    res = supabase.table('user_config').select('watchlist').eq('id', 1).execute()
    watchlist = res.data[0].get('watchlist', '')
    st.success(f"현재 감시 중인 종목: **{watchlist}**")
    st.info("파이썬애니웨어 엔진이 20초마다 새 공시를 체크하고 있습니다.")

# C. REG SHO 화면
elif st.session_state.page == 'regsho':
    if st.button("⬅️ BACK TO MENU"): go_to('home')
    st.header("⚠️ REG SHO 분석")
    st.warning("나스닥 공식 리스트 대조 기능 업데이트 중...")
    st.write("BNAI: 등재 유지 중 (예시 데이터)")

# D. 주가 검색 화면
elif st.session_state.page == 'search':
    if st.button("⬅️ BACK TO MENU"): go_to('home')
    st.header("🔍 종목 퀵 서치")
    ticker = st.text_input("조회할 티커 입력").upper()
    if ticker:
        st.write(f"**{ticker}**의 차트 및 FTD 데이터를 불러옵니다.")

# E. 설정 화면
elif st.session_state.page == 'settings':
    if st.button("⬅️ BACK TO MENU"): go_to('home')
    st.header("⚙️ 시스템 설정")
    res = supabase.table('user_config').select('watchlist').eq('id', 1).execute()
    current_val = res.data[0].get('watchlist', '')
    
    new_input = st.text_area("감시 종목 수정 (쉼표 구분)", value=current_val)
    if st.button("💾 SAVE & SYNC"):
        supabase.table('user_config').upsert({"id": 1, "watchlist": new_input}).execute()
        st.success("저장 완료!")
    
    if st.button("🔔 TEST TELEGRAM"):
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": "🔔 연결 확인!"})
