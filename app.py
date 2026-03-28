import streamlit as st
from supabase import create_client
import requests

# --- [1. 스타일 및 모바일 최적화 설정] ---
st.set_page_config(page_title="NSD PRO", layout="centered") # 모바일을 위해 centered 권장

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    
    /* 배너 버튼 슬림화 및 모바일 최적화 */
    div.stButton > button {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 10px;
        padding: 15px !important;
        height: 100px !important; /* 높이를 확 줄였습니다 */
        width: 100%;
        transition: 0.2s;
    }
    div.stButton > button:hover { border-color: #58A6FF; background-color: #1C2128; }
    div.stButton > button p { font-size: 16px !important; font-weight: bold !important; color: #58A6FF !important; }

    /* 뒤로가기 버튼 전용 스타일 (작고 심플하게) */
    .back-btn button {
        height: 40px !important;
        padding: 5px 10px !important;
        background-color: transparent !important;
        border: 1px solid #333 !important;
        width: auto !important;
        float: left;
    }
    
    /* 텍스트 가독성 */
    .status-box {
        background-color: #161B22;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #30363D;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# DB 및 텔레그램 설정
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
TOKEN = "8306599736:AAHwT_jhT9DHJqdWubOQoL1JuNlBbMjswGw"
CHAT_ID = "8182795005"

# --- [2. 로직 처리] ---
if 'page' not in st.session_state: st.session_state.page = 'home'
def go_to(page_name):
    st.session_state.page = page_name
    st.rerun()

def load_watchlist():
    try:
        res = supabase.table('user_config').select('watchlist').eq('id', 1).execute()
        return
