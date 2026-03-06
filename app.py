import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from supabase import create_client

# ==========================================
# 1. 기초 설정 및 팩트 데이터
# ==========================================
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
TELEGRAM_TOKEN = "8306599736:AAHwT_jhT9DHJqdWubOQoL1JuNlBbMjswGw"
CHAT_ID = "8182795005"

PHOTO_FACTS = {
    "AREB": 27, "VEEE": 25, "ELPW": 21, "SVRN": 20, "CISS": 19, "RVSN": 16,
    "HOOX": 15, "PBOG": 14, "SMX": 13, "UOKA": 13, "BNAI": 12, "MYCH": 12,
    "GFAI": 11, "BRTX": 10, "NCI": 10, "HUBC": 10, "DTST": 10, "HBR": 9,
    "NVDL": 9, "RIME": 9, "SOND": 9, "LFS": 8, "LGHL": 8, "PDC": 8, "KODK": 8,
    "XTKG": 7, "CDIO": 6, "GGLS": 5, "GV": 5, "MGRX": 5, "PFSA": 5, "RUBI": 5,
    "BHAT": 4, "DUOG": 3, "FFAI": 3, "AMZD": 2, "APPX": 2, "IONZ": 2,
    "WHLR": 2
}

st.set_page_config(page_title="NSD PRO", layout="wide")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================
# 2. 영구 보존 엔진 (감시 설정)
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
    except:
        st.session_state.watch_list = ""
        st.session_state.alert_on = True
    st.session_state.app_initialized = True

# ==========================================
# 3. 데이터 엔진 (나스닥 실시간 이름 반영)
# ==========================================
def fetch_verified_data():
    try:
        # DB에서 이름(security_name)을 포함해 모든 데이터를 가져옵니다.
        res = supabase.table("reg_sho_logs").select("symbol, security_name, recorded_date").gt("recorded_date", "2026-03-04").execute()
        all_df = pd.DataFrame(res.data) if res.data else pd.DataFrame()
        
        if all_df.empty:
            return pd.DataFrame()

        # 가장 최신 날짜 데이터만 필터링 (등재 제외 종목 자동 삭제 로직)
        latest_date = all_df['recorded_date'].max()
        current_symbols_data = all_df[all_df['recorded_date'] == latest_date]
        
        rows = []
        for _, entry in current_symbols_data.drop_duplicates('symbol').iterrows():
            sym = entry['symbol']
            # 일꾼이 나스닥에서 가져온 진짜 이름 사용
            real_name = entry['security_name'] if entry['security_name'] else sym
            
            # 누적 등재일 계산
            bonus_day = len(all_df[all_df['symbol'] == sym]['recorded_date'].unique())
            base_day = PHOTO_FACTS.get(sym, 0)
            
            rows.append({
                "등재일": base_day + bonus_day,
                "로고": f"https://www.google.com/s2/favicons?sz=128&domain={sym}.com",
                "티커": sym,
                "종목명": real_name
            })
        return pd.DataFrame(rows)
    except:
        return pd.DataFrame()

# ==========================================
# 4. 화면 UI (감시 + 검색)
# ==========================================
st.title("승현쓰껄~ㅋ")

# --- 🔔 감시 설정 영역 ---
with st.expander("🔔 실시간 알림 및 감시 종목 설정", expanded=False):
    col_a, col_b = st.columns([2, 1])
    with col_a:
        c_alert = st.toggle("텔레그램 알림 활성화", value=st.session_state.alert_on)
        c_watch = st.text_input("감시 티커 입력 (쉼표 구분)", value=st.session_state.watch_list).upper()
    
    if st.button("💾 설정 저장"):
        supabase.table("user_config").upsert({"id": 1, "watchlist": c_watch, "alert_enabled": c_alert}).execute()
        st.session_state.watch_list = c_watch
        st.session_state.alert_on = c_alert
        st.success("✅ 서버 저장 완료!")

# --- 🔍 데이터 검색 및 출력 ---
active_df = fetch_verified_data()
search_ticker = st.text_input("🔍 목록 내 티커 검색", "").upper()

if not active_df.empty:
    if search_ticker:
        active_df = active_df[active_df['티커'].str.contains(search_ticker)]
    
    st.dataframe(
        active_df.sort_values(by="등재일", ascending=False),
        column_order=["등재일", "로고", "티커", "종목명"],
        column_config={
            "등재일": st.column_config.NumberColumn("등재일", format="%d 일"),
            "로고": st.column_config.ImageColumn(""),
            "티커": st.column_config.TextColumn("티커"),
            "종목명": st.column_config.TextColumn("종목명")
        }, 
        use_container_width=True, hide_index=True
    )
