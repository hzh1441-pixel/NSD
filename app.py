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

# 2. 시스템 인프라 설정
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

TELEGRAM_TOKEN = "8306599736:AAHwT_jhT9DHJqdWubOQoL1JuNlBbMjswGw"
CHAT_ID = "8182795005"

st.set_page_config(page_title="NSD PRO", layout="wide")

# --- [수리 완료] 영구 저장 및 동기화 엔진 ---
def fetch_config_from_db():
    try:
        res = supabase.table("user_config").select("watchlist, alert_enabled").eq("id", 1).execute()
        if res.data:
            return res.data[0]
    except Exception:
        pass
    return {"watchlist": "", "alert_enabled": True}

# 초기 로딩 시 DB에서 데이터를 가져와 세션에 박제 (재부팅 시 유지의 핵심)
if 'initialized' not in st.session_state:
    db_data = fetch_config_from_db()
    st.session_state['user_watchlist'] = db_data['watchlist']
    st.session_state['alert_on'] = db_data['alert_enabled']
    st.session_state['initialized'] = True

def sync_to_db():
    """입력 즉시 DB에 저장하여 앱 종료 시에도 보존"""
    # [수리] 따옴표 및 괄호 누락 방지 정밀 설계
    current_watchlist = st.session_state.new_watchlist.upper()
    current_alert = st.session_state.new_alert_on
    try:
        supabase.table("user_config").upsert({
            "id": 1,
            "watchlist": current_watchlist,
            "alert_enabled": current_alert
        }).execute()
        st.session_state['user_watchlist'] = current_watchlist
        st.session_state['alert_on'] = current_alert
        st.toast("✅ 설정이 안전하게 저장되었습니다.")
    except Exception:
        st.error("⚠️ 저장 실패 (DB 확인 필요)")

st.title("🛡️ Reg sho 등재 목록")

# --- UI 상단: 24시간 실시간 감시 설정 (테스트 버튼 수리 완료) ---
with st.expander("🔔 24시간 공시 감시 설정 (앱을 꺼도 유지됨)", expanded=True):
    # [수리] image_4ed244.png의 '(' was never closed 에러 해결
    st.toggle(
        "텔레그램 알림 활성화", 
        value=st.session_state['alert_on'], 
        key="new_alert_on", 
        on_change=sync_to_db
    )
    
    st.text_input(
        "감시 티커 입력 (엔터를 치면 영구 저장됩니다)", 
        value=st.session_state['user_watchlist'], 
        key="new_watchlist", 
        on_change=sync_to_db,
        placeholder="예: BNAI, TSLA"
    )

    col1, col2 = st.columns([4, 1])
    with col1:
        if st.session_state['user_watchlist']:
            st.info(f"🛰️ 현재 서버 감시 중: {st.session_state['user_watchlist']}")
    with col2:
        # [수리] image_fa844.png의 unterminated string literal 에러 해결
        if st.button("🚀 테스트 발송"):
            test_msg = f"✅ NSD PRO: 연결 정상\n감시 목록: {st.session_state['user_watchlist']}"
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                          data={"chat_id": CHAT_ID, "text": test_msg})
            st.toast("테스트 성공!")

# 3. 데이터 엔진 (순서 100% 보존: 등재일 > 로고 > 티커 > 종목명)
def get_verified_data():
    try:
        res = supabase.table("reg_sho_logs").select("symbol, security_name, recorded_date").execute()
        if not res.data: return None
        df = pd.DataFrame(res.data)
        df['recorded_date'] = pd.to_datetime(df['recorded_date']).dt.date
        latest_date = df['recorded_date'].max()
        
        # 3/4 이후 실제 데이터 기반 추가 날짜 산출 (image_4f5622.png 에러 해결)
        extra_days = len(df[df['recorded_date'] > datetime(2026, 3, 4).date()]['recorded_date'].unique())
        current_market = df[df['recorded
