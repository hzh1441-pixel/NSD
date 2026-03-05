import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client

# 1. [완전판] 사진 속 모든 종목 전수 등록 (누락 없이 3/4 기준)
# 이제 여기에 있는 녀석들은 무조건 '✅ 사진실증'으로 뜹니다.
PHOTO_FACTS = {
    "AREB": 27, "VEEE": 25, "ELPW": 21, "SVRN": 20, "CISS": 19, "RVSN": 16, 
    "HOOX": 15, "PBOG": 14, "SMX": 13, "UOKA": 13, "BNAI": 12, "MYCH": 12, 
    "GFAI": 11, "BRTX": 10, "NCI": 10, "HUBC": 10, "DTST": 10, "HBR": 9, 
    "NVDL": 9, "RIME": 9, "LFS": 8, "LGHL": 8, "PDC": 8, "XTKG": 7, 
    "CDIO": 6, "DYTA": 5, "GGLS": 5, "GV": 5, "MGRX": 5, "PFSA": 5, "RUBI": 5,
    "BHAT": 4, "DUOG": 3, "FFAI": 3, "AMZD": 2, "APPX": 2, "IONZ": 2
}

# 인프라 설정
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="NSD PRO: ABSOLUTE FACT", layout="wide")

# --- 데이터 엔진 ---
def run_pure_engine():
    res = supabase.table("reg_sho_logs").select("symbol, security_name, recorded_date").execute()
    if not res.data: return None
    df = pd.DataFrame(res.data)
    df['recorded_date'] = pd.to_datetime(df['recorded_date'])
    latest_date = df['recorded_date'].max()
    
    # 3/4 기준 오늘 경과일 계산 (3월 5일이면 0일 유지 - 사진 데이터 확정)
    # ※ 나스닥 공식 갱신 전까진 사진 일수를 고수합니다.
    current_market = df[df['recorded_date'] == latest_date]
    
    final_rows = []
    for _, row in current_market.iterrows():
        sym = row['symbol']
        name = row['security_name'].upper()
        
        # 🔥 [ETF/펀드 필터 강화] FD, ETF, TRUST, TARGET 등 노이즈 완전 차단
        bad_keywords = ["ETF", "TRUST", "DAILY", "TARGET", "FUND", "UNIT", "FD", "DEFIANCE"]
        if any(kw in name for kw in bad_keywords): continue
        
        if sym in PHOTO_FACTS:
            # 사진에 있는 모든 종목은 이제 '✅ 사진실증'으로 강제 라벨링
            display_days = PHOTO_FACTS[sym]
            tag = "✅ 사진실증"
        else:
            display_days = len(df[df['symbol'] == sym])
            tag = "✨ 신규추적" # 진짜 사진에 없는 새로운 녀석들만

        final_rows.append({"티커": sym, "종목명": name, "등재일": display_days, "상태": tag})
            
    return pd.DataFrame(final_rows)

# --- UI ---
st.title("🛡️ Reg SHO 등재 목록")
search = st.text_input("🔍 티커 검색", "").upper()
active_df = run_pure_engine()

if active_df is not None:
    if search: active_df = active_df[active_df['티커'].str.contains(search)]
    st.dataframe(active_df.sort_values(by="등재일", ascending=False), use_container_width=True, hide_index=True)
