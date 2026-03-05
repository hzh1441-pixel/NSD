import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client
import requests

# 1. [성역] 사진 실증 마스터 데이터 (절대 수정 금지)
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

st.set_page_config(page_title="NSD PRO", layout="wide")

# --- [신규] 문자 방식 푸시 알림 엔진 (Pushover 연동) ---
def send_real_push(ticker, filing_type):
    """사용자 모바일로 문자 형태의 푸시 알림 전송"""
    # PUSHOVER_TOKEN = "사용자_토큰" 
    # PUSHOVER_USER = "사용자_키"
    # requests.post("https://api.pushover.net/1/messages.json", data={
    #     "token": PUSHOVER_TOKEN, "user": PUSHOVER_USER,
    #     "message": f"🚨 {ticker} 신규 SEC 공시: {filing_type}",
    #     "sound": "cashregister", "priority": 1
    # })
    pass

# --- UI 레이아웃 ---
st.title("🛡️ NSD PRO")

# [관심 종목 및 알림 스위치]
with st.expander("🔔 모바일 푸시 알림 설정 (문자 방식)", expanded=True):
    alert_on = st.toggle("실시간 알림 ON", value=True)
    watch_input = st.text_input("감시 티커 입력", "BNAI").upper()
    watchlist = [t.strip() for t in watch_input.split(",") if t.strip()]

# 3. 데이터 엔진 (기본 로직 유지)
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
            display_days = (PHOTO_FACTS[sym] + extra_days) if sym in PHOTO_FACTS else len(df[df['symbol'] == sym])
            
            # 🔥 [순서 고정] 등재일 > 로고 > 티커 > 종목명
            final_rows.append({
                "등재일": display_days,
                "로고": f"https://www.google.com/s2/favicons?sz=128&domain={sym}.com",
                "티커": sym,
                "종목명": name
            })
        return pd.DataFrame(final_rows)
    except: return None

# --- 실행 및 출력 ---
active_df = get_verified_data()

# 알림 트리거 (관심 종목 공시 감지 시)
if alert_on and watchlist:
    # Ortex API에서 공시 포착 시
    # send_real_push("BNAI", "8-K") 
    pass

search = st.text_input("🔍 등재 목록 내 검색", "").upper()
if active_df is not None:
    if search: active_df = active_df[active_df['티커'].str.contains(search)]
    st.dataframe(
        active_df.sort_values(by="등재일", ascending=False),
        column_config={
            "등재일": st.column_config.NumberColumn("등재일", format="%d 일"),
            "로고": st.column_config.ImageColumn(""),
            "티커": st.column_config.TextColumn("티커"),
            "종목명": st.column_config.TextColumn("종목명")
        }, use_container_width=True, hide_index=True
    )
