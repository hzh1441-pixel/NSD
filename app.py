import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client

# 1. [성역] 사진 실증 마스터 데이터 (수정 절대 금지)
PHOTO_FACTS = {
    "AREB": 27, "VEEE": 25, "ELPW": 21, "SVRN": 20, "CISS": 19, "RVSN": 16,
    "HOOX": 15, "PBOG": 14, "SMX": 13, "UOKA": 13, "BNAI": 12, "MYCH": 12,
    "GFAI": 11, "BRTX": 10, "NCI": 10, "HUBC": 10, "DTST": 10, "HBR": 9,
    "NVDL": 9, "RIME": 9, "SOND": 9, "LFS": 8, "LGHL": 8, "PDC": 8, "KODK": 8,
    "XTKG": 7, "CDIO": 6, "GGLS": 5, "GV": 5, "MGRX": 5, "PFSA": 5, "RUBI": 5,
    "BHAT": 4, "DUOG": 3, "FFAI": 3, "AMZD": 2, "APPX": 2, "IONZ": 2
}

# 2. 인프라 설정
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="NSD PRO", layout="wide")

# --- UI 상단: SEC 공시 알림 설정 (상태 보존형) ---
st.title("승현쓰껄^0^ㅋ")

# [알림 설정] 초기화 방지를 위해 session_state 활용
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = "BNAI" # 초기 1회만 설정

with st.expander("🔔 모바일 실시간 푸시 알림 설정", expanded=True):
    alert_on = st.toggle("알림 스위치 (ON/OFF)", value=True)
    # 기본값 고정 현상 해결: 사용자 입력값을 즉시 반영
    watch_input = st.text_input("감시 티커 입력 (예: BNAI, TSLA)", value=st.session_state.watchlist).upper()
    st.session_state.watchlist = watch_input
    
    if alert_on:
        st.info(f"📢 서버 감시병이 '{watch_input}' 종목을 24시간 감시합니다. 창을 닫아도 알림이 전송됩니다.")

# 3. 데이터 엔진 (로직 및 순서 고정)
def get_verified_data():
    try:
        res = supabase.table("reg_sho_logs").select("symbol, security_name, recorded_date").execute()
        if not res.data: return None
        df = pd.DataFrame(res.data)
        df['recorded_date'] = pd.to_datetime(df['recorded_date']).dt.date
        latest_date = df['recorded_date'].max()
        extra_days = len(df[df['recorded_date'] > datetime(2026, 3, 4).date()]['recorded_date'].unique())
        
        current_market = df[df['recorded_date'] == latest_date]
        final_rows = []
        for _, row in current_market.iterrows():
            sym, name = row['symbol'], row['security_name'].upper()
            if any(kw in name for kw in ["ETF", "TRUST", "FUND", "FD", "TARGET", "DAILY"]): continue
            
            # 사진 팩트 기반 등재일 산출
            display_days = (PHOTO_FACTS[sym] + extra_days) if sym in PHOTO_FACTS else len(df[df['symbol'] == sym])
            
            # 🔥 [UI 순서 고정] 등재일 > 로고 > 티커 > 종목명
            final_rows.append({
                "등재일": display_days,
                "로고": f"https://www.google.com/s2/favicons?sz=128&domain={sym}.com",
                "티커": sym,
                "종목명": name
            })
        return pd.DataFrame(final_rows)
    except: return None

active_df = get_verified_data()

# --- 하단 리스트 출력 ---
search = st.text_input("🔍 목록 내 검색", "").upper()
if active_df is not None and not active_df.empty:
    if search: active_df = active_df[active_df['티커'].str.contains(search)]
    st.dataframe(
        active_df.sort_values(by="등재일", ascending=False),
        column_config={
            "등재일": st.column_config.NumberColumn("등재일", format="%d 일", width="small"),
            "로고": st.column_config.ImageColumn("", width="small"),
            "티커": st.column_config.TextColumn("티커"),
            "종목명": st.column_config.TextColumn("종목명")
        }, use_container_width=True, hide_index=True
    )
