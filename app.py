import streamlit as st
import pandas as pd
from supabase import create_client

# 1. [절대 기준점] 사진 속 팩트 (3/4 기준)
# "함부로 13일이라고 하지 마!" -> 네, 사진에 찍힌 그대로 12일로 고정했습니다.
PHOTO_FACTS = {
    "AREB": 27, "VEEE": 25, "ELPW": 21, "SVRN": 20, "CISS": 19, "RVSN": 16,
    "HOOX": 15, "PBOG": 14, "SMX": 13, "UOKA": 13, "BNAI": 12, "MYCH": 12,
    "GFAI": 11, "BRTX": 10, "NCI": 10, "HUBC": 10, "DTST": 10, "SMCX": 2, 
    "PLTZ": 2, "NOWL": 2, "AMZD": 2, "APPX": 2, "IONZ": 2
}

# 2. 인프라 설정
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="NSD PRO: PURE FACT", layout="wide")

# --- 데이터 엔진 ---
def get_confirmed_data():
    res = supabase.table("reg_sho_logs").select("symbol, security_name, recorded_date").execute()
    if not res.data: return None
    
    df = pd.DataFrame(res.data)
    df['recorded_date'] = pd.to_datetime(df['recorded_date'])
    latest_date = df['recorded_date'].max()
    
    current_market = df[df['recorded_date'] == latest_date]
    
    final_rows = []
    for _, row in current_market.iterrows():
        sym = row['symbol']
        name = row['security_name'].upper()
        
        # [ETF 필터] 조잡한 이름들(ETF, Trust)은 여기서 컷
        bad_keywords = ["ETF", "TRUST", "DAILY", "TARGET", "FUND", "UNIT", "YIELDMAX", "DEFIANCE"]
        if any(kw in name for kw in bad_keywords): continue
        
        # [날짜 계산 로직 수정]
        # 사진에 있으면 사진값에서 시작, 3/4 이후 실제 추가된 나스닥 로그만큼만 더함
        if sym in PHOTO_FACTS:
            # 3/4 이후 실제로 나스닥 명단에 들어온 날짜 수만 카운트 (추측 금지)
            extra_days = len(df[(df['symbol'] == sym) & (df['recorded_date'] > '2026-03-04')])
            display_days = PHOTO_FACTS[sym] + extra_days
            status = "✅ 사진실증"
        else:
            display_days = len(df[df['symbol'] == sym])
            status = "⏳ 신규추적"

        final_rows.append({"티커": sym, "종목명": name, "등재일": display_days, "상태": status})
            
    return pd.DataFrame(final_rows)

# --- UI ---
st.title("🛡️ Reg SHO 실증 데이터 (추측 배제)")
search = st.text_input("🔍 티커 검색", "").upper()
active_df = get_confirmed_data()

if active_df is not None:
    if search: active_df = active_df[active_df['티커'].str.contains(search)]
    st.dataframe(active_df.sort_values(by="등재일", ascending=False), use_container_width=True, hide_index=True)
