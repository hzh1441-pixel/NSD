import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client

# 1. [절대 보존] 사진 실증 마스터 데이터 (3/4 기준)
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

# UI 설정
st.set_page_config(page_title="Reg sho 등재 목록", layout="wide")

# 로고 도메인 매핑
DOMAIN_MAP = {"BNAI": "beninc.ai", "AREB": "americanrebel.com", "VEEE": "veea.com", "RVSN": "railvision.io"}

def get_logo_url(ticker):
    domain = DOMAIN_MAP.get(ticker, f"{ticker}.com")
    return f"https://www.google.com/s2/favicons?sz=128&domain={domain}"

# --- UI 메인 ---
st.title("🛡️ Reg sho 등재 목록")

# 티커 검색창
search = st.text_input("🔍 티커 검색", "").upper()

# 3. 데이터 엔진 (로직 유지, UI 순서만 변경)
def get_verified_data():
    try:
        res = supabase.table("reg_sho_logs").select("symbol, security_name, recorded_date").execute()
        if not res.data: return None
        
        df = pd.DataFrame(res.data)
        df['recorded_date'] = pd.to_datetime(df['recorded_date']).dt.date
        latest_date = df['recorded_date'].max()
        
        # 3/4 이후 실제 추가된 공식 로그 날짜 수 (기존 로직 유지)
        extra_days = len(df[df['recorded_date'] > datetime(2026, 3, 4).date()]['recorded_date'].unique())
        
        current_market = df[df['recorded_date'] == latest_date]
        final_rows = []
        
        for _, row in current_market.iterrows():
            sym, name = row['symbol'], row['security_name'].upper()
            
            # [ETF 필터] 개별 종목이 아닌 것들 제거
            if any(kw in name for kw in ["ETF", "TRUST", "FUND", "FD", "TARGET", "DAILY"]): continue
            
            # [등재일 산출] PHOTO_FACTS 절대값 기준
            display_days = (PHOTO_FACTS[sym] + extra_days) if sym in PHOTO_FACTS else len(df[df['symbol'] == sym])

            # 🔥 [순서 변경] 등재일 > 로고 > 티
