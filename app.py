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
# 2. 영구 보존 엔진 (감시 설정 복구)
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
# 3. 데이터 엔진 (SEC 이름 + 신규 탐지)
# ==========================================
@st.cache_data(ttl=86400)
def get_sec_names():
    try:
        headers = {'User-Agent': 'NSD_PRO_Admin contact@nsdpro.com'}
        res = requests.get("https://www.sec.gov/files/company_tickers.json", headers=headers, timeout=10)
        if res.status_code == 200:
            return {item['ticker']: item['title'] for item in res.json().values()}
    except: pass
    return {}

def fetch_verified_data():
    try:
        sec_names = get_sec_names()
        res = supabase.table("reg_sho_logs").select("symbol, recorded_date").gt("recorded_date", "2026-03-04").execute()
        db_df = pd.DataFrame(res.data) if res.data else pd.DataFrame()
        
        rows = []
        processed = set()
        
        for ticker, base in PHOTO_FACTS.items():
            bonus = len(db_df[db_df['symbol'] == ticker]['recorded_date'].unique()) if not db_df.empty else 0
            rows.append({"등재일": base + bonus, "로고": f"https://www.google.com/s2/favicons?sz=128&domain={ticker}.com", "티커": ticker, "종목명": sec_names.get(ticker, ticker)})
            processed.add(ticker)
            
        if not db_df.empty:
            for ticker in db_df[~db_df['symbol'].isin(processed)]['symbol'].unique():
                bonus = len(db_df[db_df['symbol'] == ticker]['recorded_date'].unique())
                rows.append({"등재일": bonus, "로고": f"https://www.google.com/s2/favicons?sz=128&domain={ticker}.com", "티커": ticker, "종목명": sec_names.get(ticker, ticker)})
        return pd.DataFrame(rows)
    except: return pd.DataFrame()

# ==========================================
# 4. 화면 UI (감시 설정 및 검색 복구)
# ==========================================
st.title("승현쓰껄~ㅋ")

# --- 🔔 감시 설정 영역 ---
with st.expander("🔔 실시간 알림 및 감시 종목 설정", expanded=True):
    col_a, col_b = st.columns([2, 1])
    with col_a:
        current_alert = st.toggle("텔레그램 알림 활성화", value=st.session_state.alert_on)
        current_watch = st.text_input("감시 티커 입력 (쉼표 구분)", value=st.session_state.watch_list).upper()
    
    if current_alert != st.session_state.alert_on or current_watch != st.session_state.watch_list:
        supabase.table("user_config").upsert({"id": 1, "watchlist": current_watch, "alert_enabled": current_alert}).execute()
        st.session_state.watch_list = current_watch
        st.session_state.alert_on = current_alert
        st.toast("✅ 설정이 서버에 저장되었습니다.")

    if st.button("🚀 테스트 발송"):
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": f"✅ NSD PRO 연동 정상\n감시 목록: {st.session_state.watch_list}"})
        st.toast("테스트 발송 성공!")

# --- 🔍 검색 및 데이터 출력 영역 ---
df = fetch_verified_data()
search = st.text_input("🔍 목록 내 티커 검색", "").upper()

if not df.empty:
    if search:
        df = df[df['티커'].str.contains(search)]
    
    st.dataframe(
        df.sort_values(by="등재일", ascending=False),
        column_order=["등재일", "로고", "티커", "종목명"],
        column_config={
            "등재일": st.column_config.NumberColumn("등재일", format="%d 일"),
            "로고": st.column_config.ImageColumn(""),
            "티커": st.column_config.TextColumn("티커"),
            "종목명": st.column_config.TextColumn("종목명")
        },
        use_container_width=True, hide_index=True
    )
