import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client

# 1. 사진 실증 절대값 (기준: 2026-03-04)
PHOTO_FACTS = {
    "AREB": 27, "VEEE": 25, "ELPW": 21, "SVRN": 20, "CISS": 19, "RVSN": 16,
    "HOOX": 15, "PBOG": 14, "SMX": 13, "UOKA": 13, "BNAI": 12, "MYCH": 12,
    "BRTX": 10, "NCI": 10, "HBR": 9, "NVDL": 9, "RIME": 9, "LFS": 8, "LGHL": 8, "PDC": 8,
    "XTKG": 7, "CDIO": 6, "DYTA": 5, "GGLS": 5, "GV": 5, "MGRX": 5, "PFSA": 5, "RUBI": 5,
    "BHAT": 4, "DUOG": 3, "FFAI": 3, "AMZD": 2, "APPX": 2, "HIMZ": 2, "IONZ": 2
}

# 인프라 설정
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="NSD PRO: FACT MASTER", layout="wide")

# --- 데이터 엔진 ---
def run_fact_engine():
    res = supabase.table("reg_sho_logs").select("symbol, security_name, recorded_date").execute()
    if not res.data: return None, None
    
    df = pd.DataFrame(res.data)
    df['recorded_date'] = pd.to_datetime(df['recorded_date'])
    latest_date = df['recorded_date'].max()
    
    # 시간 계산 (3/4 기준)
    days_diff = (datetime.now().date() - datetime(2026, 3, 4).date()).days
    current_market = set(df[df['recorded_date'] == latest_date]['symbol'].unique())
    
    active_rows = []
    # 1단계: 오늘 시장에 있는 놈들 처리
    for sym in current_market:
        name = df[df['symbol'] == sym]['security_name'].mode()[0]
        if sym in PHOTO_FACTS:
            days = PHOTO_FACTS[sym] + days_diff
            tag = "✅ 사진실증"
        else:
            days = len(df[df['symbol'] == sym])
            tag = "✨ 신규진입" if days == 1 else "⏳ DB기록"
            
        active_rows.append({"티커": sym, "종목명": name, "등재일": days, "상태": tag})

    # 2단계: 사진에는 있었는데 오늘 명단엔 없는 '탈출자' 추출 (사용자님의 핵심 질문)
    exited_rows = []
    for sym, base in PHOTO_FACTS.items():
        if sym not in current_market:
            exited_rows.append({
                "티커": sym,
                "최종등재일": base + (days_diff - 1), # 사라지기 전날까지의 기록
                "탈출날짜": latest_date.strftime('%m-%d')
            })
            
    return pd.DataFrame(active_rows), pd.DataFrame(exited_rows)

# --- UI ---
st.title("🛡️ Reg SHO 자립형 실증 시스템")
search = st.text_input("🔍 티커 검색", "").upper()

active_df, exited_df = run_fact_engine()

if active_df is not None:
    if search: active_df = active_df[active_df['티커'].str.contains(search)]
    
    t1, t2 = st.tabs(["🔥 실시간 등재 목록", "📉 해제/삭제 데이터 추출"])
    
    with t1:
        st.dataframe(active_df.sort_values(by="등재일", ascending=False), use_container_width=True, hide_index=True)
        
    with t2:
        if not exited_df.empty:
            st.warning("⚠️ 사진 데이터 중 다음 종목들이 리스트에서 삭제되었습니다.")
            st.table(exited_df) # 여기서 데이터 추출 가능
        else:
            st.info("현재까지 사진 속 모든 종목이 생존해 있습니다.")
