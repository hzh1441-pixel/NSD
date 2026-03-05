import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client

# 1. [마스터 팩트] 개별 종목만 엄선 (ETF 제외, 3/4 기준)
# 사용자님의 명령에 따라 ETF 성격의 종목은 모두 삭제했습니다.
PHOTO_FACTS = {
    "AREB": 27, "VEEE": 25, "ELPW": 21, "SVRN": 20, "CISS": 19, "RVSN": 16, 
    "HOOX": 15, "PBOG": 14, "SMX": 13, "UOKA": 13, "BNAI": 12, "MYCH": 12, 
    "GFAI": 11, "BRTX": 10, "NCI": 10, "HUBC": 10, "DTST": 10, "HBR": 9, 
    "NVDL": 9, "RIME": 9, "LFS": 8, "LGHL": 8, "PDC": 8, "XTKG": 7, "CDIO": 6, 
    "DYTA": 5, "GGLS": 5, "GV": 5, "MGRX": 5, "PFSA": 5, "RUBI": 5, "BHAT": 4, 
    "DUOG": 3, "FFAI": 3, "AMZD": 2, "APPX": 2, "IONZ": 2
}

# 인프라 설정
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="NSD PRO: PURE STOCK", layout="wide")

# --- 데이터 엔진 ---
def run_pure_stock_engine():
    res = supabase.table("reg_sho_logs").select("symbol, security_name, recorded_date").execute()
    if not res.data: return None
    
    df = pd.DataFrame(res.data)
    df['recorded_date'] = pd.to_datetime(df['recorded_date'])
    latest_date = df['recorded_date'].max()
    
    # 시간 계산 (3/4 기준)
    days_passed = (datetime.now().date() - datetime(2026, 3, 4).date()).days
    current_market = df[df['recorded_date'] == latest_date]
    
    final_rows = []
    for _, row in current_market.iterrows():
        sym = row['symbol']
        name = row['security_name'].upper()
        
        # 🔥 [ETF 필터] 개별 종목이 아닌 것들은 여기서 컷!
        bad_keywords = ["ETF", "TRUST", "DAILY", "TARGET", "FUND", "UNIT", "YIELDMAX", "DEFIANCE"]
        if any(keyword in name for keyword in bad_keywords):
            continue # 이 녀석들은 리스트에 안 보여줍니다.
        
        if sym in PHOTO_FACTS:
            days = PHOTO_FACTS[sym] + days_passed
            tag = "✅ 사진실증"
        else:
            days = len(df[df['symbol'] == sym])
            tag = "✨ 신규진입" if days == 1 else "⏳ 추적중"
            
        final_rows.append({
            "로고": f"https://www.google.com/s2/favicons?sz=64&domain={sym}.com",
            "티커": sym,
            "종목명": name,
            "등재일": days,
            "상태": tag
        })
            
    return pd.DataFrame(final_rows)

# --- UI ---
st.title("🛡️ Reg SHO 순수 개별 종목 추적 시스템")
st.caption("ETF, Trust 등 비주식 종목은 필터링되어 제외되었습니다.")

search = st.text_input("🔍 개별 종목 티커 검색", "").upper()
active_df = run_pure_stock_engine()

if active_df is not None:
    if search: active_df = active_df[active_df['티커'].str.contains(search)]
    
    st.dataframe(
        active_df.sort_values(by="등재일", ascending=False),
        column_config={"로고": st.column_config.ImageColumn(""), "등재일": st.column_config.NumberColumn("연속 등재일", format="%d 일")},
        use_container_width=True, hide_index=True
    )
    
    st.info(f"📊 현재 {len(active_df)}개의 순수 개별 종목이 추적 중입니다.")
