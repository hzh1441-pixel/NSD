import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client
import requests

# 1. [성역] 사진 실증 마스터 데이터 (수정 절대 금지)
PHOTO_FACTS = {
    "AREB": 27, "VEEE": 25, "ELPW": 21, "SVRN": 20, "CISS": 19, "RVSN": 16,
    "HOOX": 15, "PBOG": 14, "SMX": 13, "UOKA": 13, "BNAI": 12, "MYCH": 12,
    "GFAI": 11, "BRTX": 10, "NCI": 10, "HUBC": 10, "DTST": 10, "HBR": 9,
    "NVDL": 9, "RIME": 9, "SOND": 9, "LFS": 8, "LGHL": 8, "PDC": 8, "KODK": 8,
    "XTKG": 7, "CDIO": 6, "GGLS": 5, "GV": 5, "MGRX": 5, "PFSA": 5, "RUBI": 5,
    "BHAT": 4, "DUOG": 3, "FFAI": 3, "AMZD": 2, "APPX": 2, "IONZ": 2
}

# --- 텔레그램 설정 ---
TELEGRAM_TOKEN = "8306599736:AAHwT_jhT9DHJqdWubOQoL1JuNlBbMjswGw"
CHAT_ID = "8182795005"

def send_telegram_msg(ticker, form_type, headline):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    text = f"🚨 [{ticker}] 신규 SEC 공시 포착!\n\n📌 종류: {form_type}\n📄 내용: {headline}\n⏰ 시간: {datetime.now().strftime('%H:%M:%S')}"
    try:
        res = requests.post(url, data={"chat_id": CHAT_ID, "text": text})
        return res.status_code == 200
    except:
        return False

# --- 인프라 설정 ---
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="NSD PRO", layout="wide")
st.title("승현쓰껄ㅋ")

# [핵심 수리] 입력값 영구 고정을 위한 기억 장치 초기화
if 'user_watchlist' not in st.session_state:
    st.session_state.user_watchlist = "" # 초기값은 비워둠으로써 BNAI 고정 현상 해결

# --- 상단: 실시간 감시 센터 (테스트 버튼 복구) ---
with st.expander("🔔 실시간 SEC 공시 감시 및 테스트", expanded=True):
    alert_on = st.toggle("텔레그램 알림 활성화", value=True)
    
    # 입력값 고정을 위해 key를 할당하여 session_state와 직접 연결
    watch_input = st.text_input(
        "감시 티커 입력 (예: BNAI, TSLA)", 
        value=st.session_state.user_watchlist,
        key="watchlist_input"
    ).upper()
    st.session_state.user_watchlist = watch_input
    
    col1, col2 = st.columns([4, 1])
    with col1:
        if watch_input:
            st.info(f"🛰️ 현재 감시 중: {watch_input}")
    with col2:
        # [복구] 테스트 알림 버튼
        if st.button("🚀 테스트 발송"):
            if send_telegram_msg("TEST", "CHECK", "시스템 연동 및
