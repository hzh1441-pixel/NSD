import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client
import requests

# ==========================================
# 1. 팩트 데이터 (기초 등재일 설정)
# ==========================================
PHOTO_FACTS = {
    "AREB": 27, "VEEE": 25, "ELPW": 21, "SVRN": 20, "CISS": 19, "RVSN": 16,
    "HOOX": 15, "PBOG": 14, "SMX": 13, "UOKA": 13, "BNAI": 12, "MYCH": 12,
    "GFAI": 11, "BRTX": 10, "NCI": 10, "HUBC": 10, "DTST": 10, "HBR": 9,
    "NVDL": 9, "RIME": 9, "SOND": 9, "LFS": 8, "LGHL": 8, "PDC": 8, "KODK": 8,
    "XTKG": 7, "CDIO": 6, "GGLS": 5, "GV": 5, "MGRX": 5, "PFSA": 5, "RUBI": 5,
    "BHAT": 4, "DUOG": 3, "FFAI": 3, "AMZD": 2, "APPX": 2, "IONZ": 2,
    "WHLR": 2  # 👈 확인하신 실제 등재일을 여기에 추가
}

SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"

st.set_page_config(page_title="NSD PRO", layout="wide")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================
# 2. 영구 보존 엔진 (줄 맞춤 오류 수정 완료)
# ==========================================
if "app_initialized" not in st.session_state:
    try:
        res = supabase.table("user_config").select("*").eq("id", 1).execute()
        if res.data:
            st.session_state.watch_list = res.data[0].get("watchlist", "")
            st.session_state.alert_on = res.data[0].get("alert_enabled", True)
        else:
            st.session_state.watch_list = ""
            st.session_state.alert_on = True
    except Exception:
        st.session_state.watch_list = ""
        st.session_state.alert_on = True
    st.session_state.app_initialized = True

# ==========================================
# 3. 데이터 엔진 (종목명 풀네임 복구)
# ==========================================
@st.cache_data(ttl=86400)
def get_sec_company_names():
    try:
        # SEC 보안 규정 준수 (차단 방지용 신원 정보)
        headers = {'User-Agent': 'NSD_PRO_Admin contact@nsdpro.com'}
        res = requests.get("https://www.sec.gov/files/company_tickers.json", headers=headers, timeout=10)
        if res.status_code == 200:
            return {item['ticker']: item['title'] for item in res.json().values()}
    except:
        pass
    return {}

def fetch_verified_data():
    try:
        sec_names = get_
