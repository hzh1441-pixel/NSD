import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client
import requests

# ==========================================
# 1. 팩트 데이터 및 인프라 (절대 수정 금지)
# ==========================================
PHOTO_FACTS = {
    "AREB": 27, "VEEE": 25, "ELPW": 21, "SVRN": 20, "CISS": 19, "RVSN": 16,
    "HOOX": 15, "PBOG": 14, "SMX": 13, "UOKA": 13, "BNAI": 12, "MYCH": 12,
    "GFAI": 11, "BRTX": 10, "NCI": 10, "HUBC": 10, "DTST": 10, "HBR": 9,
    "NVDL": 9, "RIME": 9, "SOND": 9, "LFS": 8, "LGHL": 8, "PDC": 8, "KODK": 8,
    "XTKG": 7, "CDIO": 6, "GGLS": 5, "GV": 5, "MGRX": 5, "PFSA": 5, "RUBI": 5,
    "BHAT": 4, "DUOG": 3, "FFAI": 3, "AMZD": 2, "APPX": 2, "IONZ": 2
}

SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
TELEGRAM_TOKEN = "8306599736:AAHwT_jhT9DHJqdWubOQoL1JuNlBbMjswGw"
CHAT_ID = "8182795005"

st.set_page_config(page_title="NSD PRO", layout="wide")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================
# 2. 영구 보존 엔진 (앱 구동 시 최초 1회만 실행)
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
# 3. UI 및 동기화
# ==========================================
st.title("승현쓰껄ㅋ")

with st.expander("🔔 실시간 알림 및 감시 종목 설정 (영구 저장)", expanded=True):
    current_alert = st.toggle("텔레그램 알림 활성화", value=st.session_state.alert_on)
    current_watch = st.text_input("감시 티커 입력 (쉼표 구분 후 엔터)", value=st.session_state.watch_list).upper()

    if current_alert != st.session_state.alert_on or current_watch != st.session_state.watch_list:
        try:
            supabase.table("user_config").upsert({
                "id": 1,
                "watchlist": current_watch,
                "alert_enabled": current_alert
            }).execute()
            
            st.session_state.watch_list = current_watch
            st.session_state.alert_on = current_alert
            st.toast("✅ 서버에 영구 저장되었습니다.")
        except Exception as e:
            st.error(f"❌ DB 저장 실패: {e}")

    col1, col2 = st.columns([4, 1])
    with col1:
        if st.session_state.watch_list:
            st.success(f"🛰️ 현재 서버 감시 중: {st.session_state.watch_list}")
    with col2:
        if st.button("🚀 테스트 발송"):
            try:
                msg = f"✅ NSD PRO: 연동 정상\n감시 목록: {st.session_state.watch_list}"
                requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                              data={"chat_id": CHAT_ID, "text": msg}, timeout=5)
                st.toast("테스트 발송 성공!")
            except Exception:
                st.error("발송 실패")

# ==========================================
# 4. 데이터 엔진
# ==========================================
def fetch_verified_data():
    try:
        res = supabase.table("reg_sho_logs").select("symbol, security_name, recorded_date").execute()
        if not res.data:
            return pd.DataFrame()
            
        df = pd.DataFrame(res.data)
        df['recorded_date'] = pd.to_datetime(df['recorded_date']).dt.date
        latest_date = df['recorded_date'].max()
        
        extra_days = len(df[df['recorded_date'] > datetime(2026, 3, 4).date()]['recorded_date'].unique())
        current_market = df[df['recorded_date'] == latest_date]
        
        rows = []
        for _, row in current_market.iterrows():
            sym = row['symbol']
            name = row['security_name'].upper()
            
            if any(kw in name for kw in ["ETF", "TRUST", "FUND", "FD", "TARGET", "DAILY"]): 
                continue
            
            days = (PHOTO_FACTS[sym] + extra_days) if sym in PHOTO_FACTS else len(df[df['symbol'] == sym])
            
            rows.append({
                "등재일": days,
                "로고": f"https://www.google.com/s2/favicons?sz=128&domain={sym}.com",
                "티커": sym,
                "종목명": name
            })
        return pd.DataFrame(rows)
    except Exception:
        return pd.DataFrame()

# ==========================================
# 5. 메인 리스트 렌더링
# ==========================================
active_df = fetch_verified_data()
search = st.text_input("🔍 목록 내 검색", "").upper()

if not active_df.empty:
    if search:
        active_df = active_df[active_df['티커'].str.contains(search)]
    
    st.dataframe(
        active_df.sort_values(by="등재일", ascending=False),
        column_order=["등재일", "로고", "티커", "종목명"],
        column_config={
            "등재일": st.column_config.NumberColumn("등재일", format="%d 일", width="small"),
            "로고": st.column_config.ImageColumn("", width="small"),
            "티커": st.column_config.TextColumn("티커"),
            "종목명": st.column_config.TextColumn("종목명")
        }, 
        use_container_width=True, 
        hide_index=True
    )
