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

# --- [절대 고장나지 않는 순차적 동기화 로직] ---
def load_db():
    try:
        res = supabase.table("user_config").select("*").eq("id", 1).execute()
        if res.data:
            return res.data[0]['watchlist'], res.data[0]['alert_enabled']
    except Exception:
        pass
    return "", True

# 앱을 켤 때 딱 한 번만 DB에서 긁어와서 기준점 생성 (재부팅 시 데이터 복구)
if 'app_init' not in st.session_state:
    saved_w, saved_a = load_db()
    st.session_state.current_watch = saved_w
    st.session_state.current_alert = saved_a
    st.session_state.app_init = True

st.title("🛡️ Reg sho 등재 목록")

with st.expander("🔔 실시간 알림 및 감시 종목 설정 (영구 저장)", expanded=True):
    
    # 1. UI 렌더링 (단순히 세션 값을 보여주기만 함)
    new_alert = st.toggle("텔레그램 알림 활성화", value=st.session_state.current_
