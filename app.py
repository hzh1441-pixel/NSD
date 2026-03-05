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

# --- [완벽 수리] 영구 저장 및 동기화 엔진 ---
def load_db_config():
    """DB에서 데이터를 가져오는 함수 (에러 발생 시 빈값 반환)"""
    try:
        res = supabase.table("user_config").select("*").eq("id", 1).execute()
        if res.data:
            return res.data[0]['watchlist'], res.data[0]['alert_enabled']
    except Exception:
        pass
    return "", True

# [핵심] 앱 구동 시 최초 1회만 DB에서 읽어와 위젯의 'key' 이름으로 세션에 저장
if 'initialized' not in st.session_state:
    db_watch, db_alert = load_db_config()
    st.session_state['input_watchlist'] = db_watch
    st.session_state['input_alert'] = db_alert
    st.session_state['initialized'] = True

def save_to_db():
    """위젯에서 엔터키나 클릭이 발생할 때 즉시 DB로 쏘는 콜백 함수"""
    new_watch = st.session_state['input_watchlist'].upper()
    new_alert = st.session_state['input_alert']
    try:
        supabase.table("user_config").upsert({
            "id": 1,
            "watchlist": new_watch,
            "alert_enabled": new_alert
        }).execute()
        st.toast("✅ 설정이 서버에 영구 저장되었습니다.")
    except Exception:
        st.error("❌ 저장 실패: DB 연결 상태를 확인하세요.")

st.title("🛡️ Reg sho 등재 목록")

# --- UI 상단: 24시간 실시간 감시 설정 ---
with st.expander("🔔 실시간 알림 및 감시 종목 설정 (영구 저장)", expanded=True):
    # [버그 해결] value 속성을 완전히 제거하고 key만 사용하여 충돌 원천 차단
    st.toggle(
        "텔레그램 알림 활성화",
        key="input_alert",
        on_change=save_to_db
    )
    
    st.text_input(
        "감시 티커 입력 (쉼표 구분 후 엔터)",
        key="input_watchlist",
        on_change=save_to_db,
        placeholder="예: BNAI, TSLA"
    )

    col1, col2 = st.columns([4, 1])
    with col1:
        if st.session_state['input_watchlist']:
            st.success(f"🛰️ 현재 서버 감시 중: {st.session_state['input_watchlist']}")
    with col2:
        if st.button("🚀 테스트 발송"):
            try:
                msg = f"✅ NSD PRO: 연동 정상\n감시 목록: {st.session_state['input_watchlist']}"
                requests.post(
                    f"https://api.
