import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from supabase import create_client

# ==========================================
# 1. 기초 설정 및 인프라
# ==========================================
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
TELEGRAM_TOKEN = "8306599736:AAHwT_jhT9DHJqdWubOQoL1JuNlBbMjswGw"
CHAT_ID = "8182795005"

# [팩트] 고정 감시 명단 및 기초 등재일
PHOTO_FACTS = {
    "AREB": 27, "VEEE": 25, "ELPW": 21, "SVRN": 20, "CISS": 19, "RVSN": 16,
    "HOOX": 15, "PBOG": 14, "SMX": 13, "UOKA": 13, "BNAI": 12, "MYCH": 12,
    "GFAI": 11, "BRTX": 10, "NCI": 10, "HUBC": 10, "DTST": 10, "HBR": 9,
    "NVDL": 9, "RIME": 9, "SOND": 9, "LFS": 8, "LGHL": 8, "PDC": 8, "KODK": 8,
    "XTKG": 7, "CDIO": 6, "GGLS": 5, "GV": 5, "MGRX": 5, "PFSA": 5, "RUBI": 5,
    "BHAT": 4, "DUOG": 3, "FFAI": 3, "AMZD": 2, "APPX": 2, "IONZ": 2,
    "WHLR": 2  # 👈 WHLR이 확실히 포함되었습니다.
}

st.set_page_config(page_title="NSD PRO", layout="wide")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================
# 2. 상태 관리 및 설정 로드
# ==========================================
if "app_initialized" not in st.session_state:
    try:
        res = supabase.table("user_config").select("*").eq("id", 1).execute()
        if res.data:
            st.session_state.watch_list =
