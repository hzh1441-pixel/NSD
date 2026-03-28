import streamlit as st
from supabase import create_client
import requests
import pandas as pd

# --- [1. 스타일 및 세련된 레이아웃 설정] ---
st.set_page_config(page_title="NSD PRO MASTER", layout="wide")

# 래빗스탁 스타일 커스텀 CSS (카드형 배너 디자인)
st.markdown("""
    <style>
    /* 전체 배경 및 폰트 */
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    
    /* 카드형 배너 스타일 */
    .banner-container {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        transition: 0.2s;
    }
    .banner-container:hover {
        border-color: #58A6FF;
        background-color: #1C2128;
    }
    .banner-title {
        font-size: 18px;
        font-weight: bold;
        color: #58A6FF;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .banner-status {
        font-size: 12px;
        padding: 2px 8px;
        border-radius: 20px;
        background-color: #238636;
        color: white;
    }
    
    /* 사이드바 스타일 */
    section[data-testid="stSidebar"] { background-color: #0D1117; border-right: 1px solid #30363D; }
    
    /* 에러 났던 스페이서 대체용 */
    .spacer { margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

# DB 및 텔레그램 설정
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
TOKEN = "8306599736:AAHwT_jhT9DHJqdWubOQoL1JuNlBbMjswGw"
CHAT_ID = "8182795005"

# --- [2. 데이터 로드 로직] ---
def load_watchlist():
    try:
        res = supabase.table('user_config').select('watchlist').eq('id', 1).execute()
        return res.data[0].get('watchlist', '') if res.data else ""
    except: return ""

# --- [3. 사이드바 내비게이션] ---
with st.sidebar:
    st.markdown("<h2 style='color: #58A6FF;'>🛡️ NSD PRO</h2>", unsafe_allow_html=True)
    st.caption("실시간 나스닥 터미널 v2.0")
    st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
    
    menu = st.radio(
        "카테고리 선택",
        ["🏠 대시보드 홈", "📡 SEC 공시 센터", "⚠️ Reg Sho 분석", "🔍 종목 퀵 검색", "⚙️ 시스템 설정"],
        index=0
    )

# --- [4. 메인 화면 구성] ---

current_watchlist = load_watchlist()
tickers = [t.strip().upper() for t in current_watchlist.split(',') if t.strip()]

if menu == "🏠 대시보드 홈":
    st.title("📊 실시간 모니터링 현황")
    
    # 상단 요약 배너 4개 그리드 배치
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'''<div class="banner-container">
            <div class="banner-title">📡 SEC 감시 <span class="banner-status">ON</span></div>
            <div style="font-size: 24px; font-weight: bold;">{len(tickers)} 종목</div>
        </div>''', unsafe_allow_html=True)

    with col2:
        st.markdown(f'''<div class="banner-container">
            <div class="banner-title" style="color: #F2CC60;">⚠️ Reg Sho</div>
            <div style="font-size: 24px; font-weight: bold;">분석 중</div>
        </div>''', unsafe_allow_html=True)

    with col3:
        st.markdown(f'''<div class="banner-container">
            <div class="banner-title" style="color: #79C0FF;">🔍 FTD 데이터</div>
            <div style="font-size: 24px; font-weight: bold;">연결됨</div>
        </div>''', unsafe_allow_html=True)

    with col4:
        st.markdown(f'''<div class="banner-container">
            <div class="banner-title" style="color: #FF7B72;">⚙️ 서버 상태</div>
            <div style="font-size: 24px; font-weight: bold;">정상</div>
        </div>''', unsafe_allow_html=True)

    # 중앙 데이터 배너
    st.markdown('<div class="banner-container"><div class="banner-title">📋 현재 실시간 감시 리스트</div>', unsafe_allow_html=True)
    if tickers:
        st.write(", ".join(tickers))
    else:
        st.write("감시 중인 종목이 없습니다.")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "⚙️ 시스템 설정":
    st.title("⚙️ 시스템 설정")
    
    with st.container():
        st.markdown('<div class="banner-container">', unsafe_allow_html=True)
        st.subheader("🛠️ 감시 종목 업데이트")
        new_tickers = st.text_area("티커를 입력하세요 (쉼표 구분)", value=current_watchlist, height=100)
        if st.button("💾 설정 저장 및 동기화"):
            supabase.table('user_config').upsert({"id": 1, "watchlist": new_tickers}).execute()
            st.success("✅ 저장되었습니다.")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="banner-container">', unsafe_allow_html=True)
        st.subheader("🔔 텔레그램 테스트")
        if st.button("테스트 메시지 발송"):
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": "🔔 연결 확인 성공!"})
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.title(menu)
    st.info(f"현재 '{menu}' 기능의 세부 데이터 연동을 준비 중입니다.")
