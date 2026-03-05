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

# --- 영구 보존 엔진: DB에서 설정 불러오기 ---
def get_config_from_db():
    try:
        res = supabase.table("user_config").select("watchlist, alert_enabled").eq("id", 1).execute()
        if res.data:
            return res.data[0]
    except Exception:
        pass
    return {"watchlist": "", "alert_enabled": True}

# 앱 시작 시 초기화 (재부팅 시 데이터 복구의 핵심)
if 'initialized' not in st.session_state:
    db_cfg = get_config_from_db()
    st.session_state['watchlist'] = db_cfg['watchlist']
    st.session_state['alert_enabled'] = db_cfg['alert_enabled']
    st.session_state['initialized'] = True

# 저장 함수: 입력 즉시 DB에 동기화
def sync_db_config():
    try:
        # 입력창(key="w_input")과 토글(key="a_toggle")의 최신 값을 DB에 저장
        w_val = st.session_state.w_input.upper()
        a_val = st.session_state.a_toggle
        supabase.table("user_config").upsert({
            "id": 1,
            "watchlist": w_val,
            "alert_enabled": a_val
        }).execute()
        # 세션 상태도 최신화
        st.session_state['watchlist'] = w_val
        st.session_state['alert_enabled'] = a_val
        st.toast("
