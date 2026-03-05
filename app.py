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
    """텔레그램 팝업 전송 함수"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    text = f"🚨 [{ticker}] 신규 SEC 공시 포착!\n\n📌 종류: {form_type}\n📄 내용: {headline}"
    try:
        res = requests.post(url, data={"chat_id": CHAT_ID, "text": text}, timeout=10)
        return res.status_code == 200
    except:
        return False

# --- 인프라 설정 ---
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Reg sho 등재 목록", layout="wide")

# [입력값 고정 로직] 껐다 켜도 유지되도록 설정
if 'user_watchlist' not in st.session_state:
    st.session_state.user_watchlist = ""

# --- UI 상단: 감시 센터 ---
st.title("^0^ㅋ")

with st.expander("🔔 실시간 SEC 공시 감시 및 테스트", expanded=True):
    alert_on = st.toggle("텔레그램 알림 활성화", value=True)
    
    # BNAI 고정 현상 해결 및 입력값 기억
    watch_input = st.text_input(
        "감시 티커 입력 (쉼표 구분)", 
        value=st.session_state.user_watchlist,
        placeholder="감시할 티커를 입력하세요"
    ).upper()
    st.session_state.user_watchlist = watch_input
    
    col1, col2 = st.columns([4, 1])
    with col1:
        if watch_input:
            st.success(f"🛰️ 현재 감시 중인 목록: {watch_input}")
    with col2:
        # [복구] 테스트 알림 버튼 (오타 및 따옴표 오류 수정)
        if st.button("🚀 테스트 발송"):
            if send_telegram_msg("TEST", "CHECK", "시스템 연동 및 UI 순서 보존 성공"):
                st.toast("텔레그램 발송 성공!")
            else:
                st.error("발송 실패")

# 3. 데이터 엔진 (로직 및 순서 100% 보존)
def get_verified_data():
    try:
        res = supabase.table("reg_sho_logs").select("symbol, security_name, recorded_date").execute()
        if not res.data: return None
        df = pd.DataFrame(res.data)
        df['recorded_date'] = pd.to_datetime(df['recorded_date']).dt.date
        latest_date = df['recorded_date'].max()
        
        # 3/4 이후 실제 데이터 기반 추가 날짜 산
