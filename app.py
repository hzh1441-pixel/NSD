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

# --- [영구 저장 로직] 앱이 켜질 때 DB에서 마지막 기록을 강제로 가져옴 ---
@st.cache_data(ttl=5) # 짧은 캐시로 DB 부하 방지 및 최신화
def fetch_saved_config():
    try:
        res = supabase.table("user_config").select("watchlist, alert_enabled").eq("id", 1).execute()
        if res.data:
            return res.data[0]
    except:
        pass
    return {"watchlist": "", "alert_enabled": True}

# 초기화 로직: 앱이 켜지자마자 실행
saved_data = fetch_saved_config()
if 'user_watchlist' not in st.session_state:
    st.session_state.user_watchlist = saved_data['watchlist']
if 'alert_on' not in st.session_state:
    st.session_state.alert_on = saved_data['alert_enabled']

def update_config():
    """사용자가 입력값을 바꾸는 즉시 DB에 영구 저장"""
    try:
        supabase.table("user_config").upsert({
            "id": 1,
            "watchlist": st.session_state.new_watchlist,
            "alert_enabled": st.session_state.new_alert_on
        }).execute()
        st.session_state.user_watchlist = st.session_state.new_watchlist
        st.session_state.alert_on = st.session_state.new_alert_on
    except:
        pass

st.title("🛡️ Reg sho 등재 목록")

# --- UI 상단: 24시간 실시간 감시 설정 ---
with st.expander("🔔 24시간 공시 감시 설정 (앱을 꺼도 유지됨)", expanded=True):
    # 알림 스위치와 티커 입력창을 DB 값과 동기화
    alert_on = st.toggle(
        "텔레그램 알림 활성화", 
        value=st.session_state.alert_on, 
        key="new_alert_on", 
        on_change=update_config
    )
    
    watch_input = st.text_input(
        "감시 티커 입력 (쉼표 구분)", 
        value=st.session_state.user_watchlist, 
        key="new_watchlist", 
        on_change=update_config,
        placeholder="예: BNAI, TSLA"
    ).upper()

    col1, col2 = st.columns([4, 1])
    with col1:
        if st.session_state.user_watchlist:
            st.success(f"🛰️ 현재 서버 감시 중: {st.session_state.user_watchlist}")
    with col2:
        if st.button("🚀 테스트 발송"):
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                          data={"chat_id": CHAT_ID, "text": f"✅ 연결 및 영구 저장 정상\n감시 목록: {st.session_state.user_watchlist}"})
            st.toast("테스트 성공!")

# 3. 데이터 엔진 (로직 및 순서 100% 보존: 등재일 > 로고 > 티커 > 종목명)
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
            
            days = (PHOTO_FACTS[sym] + extra_days) if sym in PHOTO_FACTS else len(df[df['symbol'] == sym])
            
            # 🔥 [UI 순서 절대 고정] 등재일 > 로고 > 티커 > 종목명
            final_rows.append({
                "등재일": days,
                "로고": f"https://www.google.com/s2/favicons?sz=128&domain={sym}.com",
                "티커": sym,
                "종목명": name
            })
        return pd.DataFrame(final_rows)
    except: return None

# 데이터 출력 영역
active_df = get_verified_data()
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
