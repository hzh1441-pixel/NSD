import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client

# 1. 사진 팩트 (기준: 2026-03-04)
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

st.set_page_config(page_title="NSD PRO: TOTAL TRACKER", layout="wide")

# --- 데이터 통합 처리 ---
res = supabase.table("reg_sho_logs").select("symbol, security_name, recorded_date").execute()

if res.data:
    df = pd.DataFrame(res.data)
    df['recorded_date'] = pd.to_datetime(df['recorded_date'])
    latest_date = df['recorded_date'].max()
    
    # [팩트 체크 환경]
    current_market_list = set(df[df['recorded_date'] == latest_date]['symbol'].unique())
    days_passed = (datetime.now().date() - datetime(2026, 3, 4).date()).days
    
    final_rows = []

    for sym in current_market_list:
        name = df[df['symbol'] == sym]['security_name'].iloc[0]
        
        # A. 사진 팩트 종목 (절대값 우선)
        if sym in PHOTO_FACTS:
            actual_days = PHOTO_FACTS[sym] + days_passed
            tag = "✅ 실증(사진)"
        else:
            # B. 기존 DB 추적 종목 vs C. 신규 진입 종목 판별
            db_count = len(df[df['symbol'] == sym])
            actual_days = db_count
            
            if db_count == 1:
                tag = "✨ 신규 진입" # 오늘 처음 발견됨
            else:
                tag = "⏳ DB 추적 중"

        final_rows.append({
            "티커": sym,
            "종목명": name,
            "누적 등재일": actual_days,
            "구분": tag
        })

    # --- UI 출력 ---
    st.title("🛡️ Reg SHO 통합 실증 시스템")
    
    # 1. 전체 등재 리스트 (정렬 가능)
    st.subheader("📊 현재 등재 종목 (실시간 팩트 반영)")
    ranking_df = pd.DataFrame(final_rows).sort_values(by="누적 등재일", ascending=False)
    st.dataframe(ranking_df, use_container_width=True, hide_index=True)
    
    # 2. 신규 진입 종목만 따로 추출해서 보여주기
    new_entries = [row for row in final_rows if row["구분"] == "✨ 신규 진입"]
    if new_entries:
        st.toast(f"오늘 {len(new_entries)}개의 신규 종목이 등재되었습니다!")
        with st.expander("🆕 오늘의 신규 진입 종목 확인"):
            st.table(pd.DataFrame(new_entries)[["티커", "종목명"]])

    st.info(f"💡 사진 팩트 기반 합산과 신규 진입 탐지가 동시에 가동 중입니다. (BNAI: {PHOTO_FACTS['BNAI']+days_passed}일)")
