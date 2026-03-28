import streamlit as st
from supabase import create_client
import pandas as pd
import requests

# --- [1. 스타일 및 설정] ---
st.set_page_config(page_title="NSD PRO MASTER", layout="wide")

# 배너 스타일을 위한 커스텀 CSS
st.markdown("""
    <style>
    .banner-card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #00FFAA;
        margin-bottom: 20px;
    }
    .banner-title {
        color: #00FFAA;
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# DB 연결
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
TOKEN = "8306599736:AAHwT_jhT9DHJqdWubOQoL1JuNlBbMjswGw"
CHAT_ID = "8182795005"

# --- [2. 핵심 로직] ---
def load_data():
    res = supabase.table('user_config').select('watchlist').eq('id', 1).execute()
    return res.data[0].get('watchlist', '') if res.data else ""

# --- [3. 메인 배너 레이아웃] ---

# 메인 타이틀
st.title("🛡️ NSD PRO : REAL-TIME TERMINAL")
st.divider()

# 좌측/우측 정밀 배너 배치
left_col, right_col = st.columns([2, 1])

with left_col:
    # --- 배너 1: SEC 공시 모니터링 ---
    st.markdown('<div class="banner-card"><div class="banner-title">📡 [BANNER 01] SEC REAL-TIME MONITORING</div>', unsafe_allow_html=True)
    watchlist_str = load_data()
    tickers = [t.strip().upper() for t in watchlist_str.split(',') if t.strip()]
    
    c1, c2, c3 = st.columns(3)
    for i, t in enumerate(tickers[:3]): # 상위 3개 종목 요약 표시
        with [c1, c2, c3][i]:
            st.metric(label=f"TARGET", value=t, delta="ACTIVE")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- 배너 2: REG SHO 추적기 ---
    st.markdown('<div class="banner-card"><div class="banner-title">⚠️ [BANNER 02] REG SHO THRESHOLD TRACKER</div>', unsafe_allow_html=True)
    # 실제 데이터 연동 전 시각화 예시
    reg_data = pd.DataFrame({
        "Ticker": tickers if tickers else ["-"],
        "Status": ["ON LIST" if "BNAI" in t or "EMPD" in t else "CLEAN" for t in (tickers if tickers else ["-"])],
        "Consecutive Days": ["8 Days" if "BNAI" in t else "-" for t in (tickers if tickers else ["-"])]
    })
    st.table(reg_data)
    st.markdown('</div>', unsafe_allow_html=True)

with right_col:
    # --- 배너 3: 종목 시세 검색 ---
    st.markdown('<div class="banner-card" style="border-left-color: #FFCC00;"><div class="banner-title" style="color: #FFCC00;">🔍 [BANNER 03] QUICK PRICE SEARCH</div>', unsafe_allow_html=True)
    search_q = st.text_input("티커 입력 (예: AAPL)", "").upper()
    if search_q:
        st.write(f"**{search_q}** 시세 데이터 연결 중...")
        st.info("Yahoo Finance API 연동 시 실시간 차트가 이곳에 표시됩니다.")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- 배너 4: 시스템 컨트롤 ---
    st.markdown('<div class="banner-card" style="border-left-color: #FF4B4B;"><div class="banner-title" style="color: #FF4B4B;">⚙️ [BANNER 04] SYSTEM CONTROL</div>', unsafe_allow_html=True)
    new_input = st.text_area("감시 종목 수정", value=watchlist_str, height=100)
    
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("💾 SAVE SETTINGS"):
            supabase.table('user_config').upsert({"id": 1, "watchlist": new_input}).execute()
            st.success("SAVED")
            st.rerun()
    with btn_col2:
        if st.button("🔔 TEST ALARM"):
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": "🔔 NSD PRO 연결 확인!"})
    st.markdown('</div>', unsafe_allow_html=True)

# 하단 푸터
st.markdown("---")
st.caption(f"SERVER STATUS: OPERATIONAL | UTC: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
