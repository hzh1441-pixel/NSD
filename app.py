import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client

# 1. [데이터 로직] 절대값 데이터 (기존과 동일, 수정 없음)
PHOTO_FACTS = {
    "AREB": 27, "VEEE": 25, "ELPW": 21, "SVRN": 20, "CISS": 19, "RVSN": 16,
    "HOOX": 15, "PBOG": 14, "SMX": 13, "UOKA": 13, "BNAI": 12, "MYCH": 12,
    "GFAI": 11, "BRTX": 10, "NCI": 10, "HUBC": 10, "DTST": 10, "HBR": 9,
    "NVDL": 9, "RIME": 9, "SOND": 9, "LFS": 8, "LGHL": 8, "PDC": 8, "KODK": 8,
    "XTKG": 7, "CDIO": 6, "GGLS": 5, "GV": 5, "MGRX": 5, "PFSA": 5, "RUBI": 5,
    "BHAT": 4, "DUOG": 3, "FFAI": 3, "AMZD": 2, "APPX": 2, "IONZ": 2
}

# 2. 시스템 인프라
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="NSD PRO", layout="wide")

# --- UI 레이아웃 ---
st.title("🛡️ NSD PRO: REG SHO MONITOR")

# 검색창 (깔끔한 배치)
search = st.text_input("Search Ticker", "").upper()

# --- 데이터 엔진 (UI 출력용 정제) ---
def get_clean_display_data():
    res = supabase.table("reg_sho_logs").select("symbol, security_name, recorded_date").execute()
    if not res.data: return None
    
    df = pd.DataFrame(res.data)
    df['recorded_date'] = pd.to_datetime(df['recorded_date'])
    latest_date = df['recorded_date'].max()
    
    # 3/4 사진 기준, 실제 나스닥 업데이트가 발생한 날짜 수 계산
    # (억측 방지를 위해 DB에 쌓인 고유 날짜 중 3/4 이후만 카운트)
    extra_days = len(df[df['recorded_date'] > '2026-03-04']['recorded_date'].unique())
    
    current_market = df[df['recorded_date'] == latest_date]
    final_rows = []
    
    for _, row in current_market.iterrows():
        sym, name = row['symbol'], row['security_name'].upper()
        
        # ETF/노이즈 필터링 (기존 로직 유지)
        if any(kw in name for kw in ["ETF", "TRUST", "FUND", "FD", "TARGET", "DAILY", "YIELDMAX"]):
            continue
            
        # 등재일 결정
        if sym in PHOTO_FACTS:
            display_days = PHOTO_FACTS[sym] + extra_days
        else:
            display_days = len(df[df['symbol'] == sym])

        final_rows.append({
            "Logo": f"https://www.google.com/s2/favicons?sz=64&domain={sym}.com",
            "Ticker": sym,
            "Security Name": name,
            "Days": display_days
        })
            
    return pd.DataFrame(final_rows)

display_df = get_clean_display_data()

if display_df is not None:
    if search:
        display_df = display_df[display_df['Ticker'].str.contains(search)]
    
    # 표 출력 (조잡한 문구 삭제, 로고 전진 배치)
    st.dataframe(
        display_df.sort_values(by="Days", ascending=False),
        column_config={
            "Logo": st.column_config.ImageColumn("", width="small"),
            "Ticker": st.column_config.TextColumn("Ticker"),
            "Security Name": st.column_config.TextColumn("Security Name"),
            "Days": st.column_config.NumberColumn("Continuous Days", format="%d Days")
        },
        use_container_width=True,
        hide_index=True
    )
