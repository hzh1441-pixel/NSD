import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client

# 1. [절대 기준] 사용자 사진 실증 데이터 (기록값 절대 보존)
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

# UI 제목 설정
st.set_page_config(page_title="Reg sho 등재 목록", layout="wide")

# 로고 도메인 매핑 (로고 누락 방지용)
DOMAIN_MAP = {"BNAI": "beninc.ai", "AREB": "americanrebel.com", "VEEE": "veea.com", "RVSN": "railvision.io"}

def get_logo_url(ticker):
    domain = DOMAIN_MAP.get(ticker, f"{ticker}.com")
    return f"https://www.google.com/s2/favicons?sz=128&domain={domain}"

# --- 메인 화면 ---
st.title("🛡️ Reg sho 등재 목록")

# [복구] 한글 검색창
search = st.text_input("🔍 티커 검색", "").upper()

# 데이터 엔진 (로직 망가뜨리지 않음)
def get_verified_data():
    try:
        res = supabase.table("reg_sho_logs").select("symbol, security_name, recorded_date").execute()
        if not res.data:
            return None
        
        df = pd.DataFrame(res.data)
        df['recorded_date'] = pd.to_datetime(df['recorded_date'])
        latest_date = df['recorded_date'].max()
        
        # 3/4 이후 실제 로그가 찍힌 날짜 수 (오늘 날짜와 무관하게 실제 데이터 기준)
        extra_days = len(df[df['recorded_date'] > '2026-03-04']['recorded_date'].unique())
        
        current_market = df[df['recorded_date'] == latest_date]
        final_rows = []
        
        for _, row in current_market.iterrows():
            sym, name = row['symbol'], row['security_name'].upper()
            
            # ETF 및 노이즈 필터링
            if any(kw in name for kw in ["ETF", "TRUST", "FUND", "FD", "TARGET", "DAILY"]):
                continue
            
            # 등재일 산출 (기존 코딩값 엄수)
            if sym in PHOTO_FACTS:
                display_days = PHOTO_FACTS[sym] + extra_days
            else:
                display_days = len(df[df['symbol'] == sym])

            final_rows.append({
                "로고": get_logo_url(sym),
                "티커": sym,
                "종목명": name,
                "등재일": display_days
            })
        return pd.DataFrame(final_rows)
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {e}")
        return None

# 데이터 호출 및 출력
active_df = get_verified
