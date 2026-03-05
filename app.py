import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client
import requests

# 1. [절대값] 메인 자료 코딩값 (절대 수정 금지 - 3/4 사진 팩트 유지)
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

# [UI 설정]
st.set_page_config(page_title="Reg sho 등재 목록", layout="wide")

# 3. 로고 추출 엔진 (Ortex 및 금융 API 기반)
def get_logo(ticker):
    # Ortex Metadata/Ticker 기반 고해상도 로고 서비스 활용
    # 티커만으로 가장 정확한 로고를 반환하는 금융 전용 CDN을 사용합니다.
    return f"https://img.logo.dev/ticker/{ticker}?token=pk_ST8tG_X9R2C1O1J_W3S3" # 예시 토큰 포함 경로

# --- UI 메인 ---
st.title("🛡️ Reg sho 등재 목록")

# [복구] 티커 검색창
search = st.text_input("🔍 티커 검색", "").upper()

# 데이터 엔진 (기존 로직 및 코딩값 절대 보존)
def get_display_data():
    res = supabase.table("reg_sho_logs").select("symbol, security_name, recorded_date").execute()
    if not res.data: return None
    
    df = pd.DataFrame(res.data)
    df['recorded_date'] = pd.to_datetime(df['recorded_date'])
    latest_date = df['recorded_date'].max()
    
    # 3/4 이후 실제 로그 발생 수 합산 (추측 방지)
    extra_days = len(df[df['recorded_date'] > '2026-03-04']['recorded_date'].unique())
    current_market = df[df['recorded_date'] == latest_date]
    
    final_rows = []
    for _, row in current_market.iterrows():
        sym, name = row['symbol'], row['security_name'].upper()
        
        # ETF/Trust 필터링 (기존 로직 유지)
        if any(kw in name for kw in ["ETF", "TRUST", "FUND", "FD", "TARGET", "DAILY"]): continue
        
        # 등재일 산출 (PHOTO_FACTS 절대값 기준)
        if sym in PHOTO_FACTS:
            display_days = PHOTO_FACTS[sym] + extra_days
        else:
            display_days = len(df[df['symbol'] == sym])

        final_rows.append({
            "로고": get_logo(sym),
            "티커": sym,
            "종목명": name,
            "등재일": display_days
        })
            
    return pd.DataFrame(final_rows)

active_df = get_display_data()

if active_df is not None:
    if search:
        active_df = active_df[active_df['티커'].str.contains(search)]
    
    # [UI 최종 정리] 로고 전진 배치 및 요청하신 명칭 적용
    st.dataframe(
        active_df.sort_values(by="등재일", ascending=False),
        column_config={
            "로고": st.column_config.ImageColumn("", width="small"),
            "티커": st.column_config.TextColumn("티커"),
            "종목명": st.column_config.TextColumn("종목명"),
            "등재일": st.column_config.NumberColumn("등재일", format="%d 일")
        },
        use_container_width=True,
        hide_index=True
    )
