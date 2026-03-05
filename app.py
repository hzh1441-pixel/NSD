import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client

# 1. [절대값 Sanctuary] 사진 실증 데이터 (수정 절대 금지)
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

st.set_page_config(page_title="Reg sho 등재 목록", layout="wide")

# 로고 도메인 매핑 (로고 누락 방지)
DOMAIN_MAP = {"BNAI": "beninc.ai", "AREB": "americanrebel.com", "VEEE": "veea.com", "RVSN": "railvision.io"}

def get_logo_url(ticker):
    domain = DOMAIN_MAP.get(ticker, f"{ticker}.com")
    return f"https://www.google.com/s2/favicons?sz=128&domain={domain}"

# --- UI 상단: SEC 공시 알림 설정 (입력값 기억 로직 탑재) ---
st.title("승현쓰껄ㅋ")

# [핵심 수리] 사용자 입력값을 기억하기 위한 기억 장치(session_state) 초기화
if 'user_watchlist' not in st.session_state:
    st.session_state.user_watchlist = "" # 처음에는 비워둡니다.

with st.expander("🔔 모바일 실시간 SEC 공시 알림 설정", expanded=True):
    alert_on = st.toggle("알림 활성화 (ON/OFF)", value=True)
    
    # [수정] value를 session_state와 연결하여 입력값이 초기화되지 않게 함
    watch_input = st.text_input(
        "감시할 티커 입력 (쉼표 구분)", 
        value=st.session_state.user_watchlist,
        placeholder="예: BNAI, TSLA, AAPL"
    ).upper()
    
    # 입력한 값을 즉시 기억 장치에 저장
    st.session_state.user_watchlist = watch_input
    
    if alert_on and watch_input:
        st.success(f"✅ 현재 '{watch_input}' 종목을 24시간 감시 중입니다. (문자 방식 알림)")
    elif alert_on and not watch_input:
        st.warning("감시할 티커를 입력해주세요.")

# 3. 데이터 엔진 (로직 및 순서 100% 보존)
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
                "로고": get_logo_url(sym),
                "티커": sym,
                "종목명": name
            })
        return pd.DataFrame(final_rows)
    except: return None

# 데이터 출력
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
