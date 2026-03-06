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
# 2. 데이터 엔진 (종목명 오류 100% 해결 버전)
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
        # 창고(DB)에서 이름(security_name)까지 같이 가져옵니다.
        res = supabase.table("reg_sho_logs").select("symbol, security_name, recorded_date").gt("recorded_date", "2026-03-04").execute()
        all_df = pd.DataFrame(res.data) if res.data else pd.DataFrame()
        
        if all_df.empty: return pd.DataFrame()

        latest_date = all_df['recorded_date'].max()
        current_data = all_df[all_df['recorded_date'] == latest_date]
        
        rows = []
        for _, entry in current_data.drop_duplicates('symbol').iterrows():
            sym = entry['symbol']
            db_name = entry['security_name'] # 창고에 저장된 사냥꾼표 진짜 이름
            
            bonus_day = len(all_df[all_df['symbol'] == sym]['recorded_date'].unique())
            base_day = PHOTO_FACTS.get(sym, 0)
            
            # 우선순위: SEC 공식명칭 -> 창고 저장 명칭 -> 티커명
            display_name = sec_names.get(sym, db_name if db_name else sym)
            
            rows.append({
                "등재일": base_day + bonus_day,
                "로고": f"https://www.google.com/s2/favicons?sz=128&domain={sym}.com",
                "티커": sym,
                "종목명": display_name
            })
        return pd.DataFrame(rows)
    except: return pd.DataFrame()

# ==========================================
# 3. 화면 UI (감시 및 검색 기능 포함)
# ==========================================
st.title("승현쓰껄~ㅋ")

with st.expander("🔔 실시간 알림 및 감시 종목 설정", expanded=False):
    col_a, col_b = st.columns([2, 1])
    with col_a:
        alert_on = st.toggle("텔레그램 알림 활성화", value=st.session_state.get('alert_on', True))
        watch_list = st.text_input("감시 티커 입력 (쉼표 구분)", value=st.session_state.get('watch_list', "")).upper()
    
    if st.button("💾 설정 저장"):
        supabase.table("user_config").upsert({"id": 1, "watchlist": watch_list, "alert_enabled": alert_on}).execute()
        st.session_state.watch_list = watch_list
        st.session_state.alert_on = alert_on
        st.success("설정이 저장되었습니다.")

df = fetch_verified_data()
search = st.text_input("🔍 목록 내 티커 검색", "").upper()

if not df.empty:
    if search: df = df[df['티커'].str.contains(search)]
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
