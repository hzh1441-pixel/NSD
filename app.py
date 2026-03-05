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
    st.session_state.user_watchlist = db_data['watchlist']
    st.session_state.alert_on = db_data['alert_enabled']
    st.session_state.initialized = True

def sync_to_db():
    """입력 즉시 DB에 저장하여 앱 종료 시에도 보존"""
    current_watchlist = st.session_state.new_watchlist.upper()
    current_alert = st.session_state.new_alert_on
    try:
        supabase.table("user_config").upsert({
            "id": 1,
            "watchlist": current_watchlist,
            "alert_enabled": current_alert
        }).execute()
        st.session_state.user_watchlist = current_watchlist
        st.session_state.alert_on = current_alert
        st.toast("✅ 설정이 안전하게 저장되었습니다.")
    except Exception:
        st.error("⚠️ 저장 실패 (DB 확인 필요)")

st.title("🛡️ Reg sho 등재 목록")

# --- UI 상단: 24시간 실시간 감시 설정 (테스트 버튼 복구) ---
with st.expander("🔔 24시간 공시 감시 설정 (앱을 꺼도 유지됨)", expanded=True):
    st.toggle(
        "텔레그램 알림 활성화", 
        value=st.session_state.alert_on,
