import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client

# 1. [절대 보존] 사진 실증 마스터 데이터 (3/4 기준)
# BNAI는 12일이며, 이 숫자는 시스템의 뿌리입니다. (수정 금지)
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

# 로고 도메인 매핑 (로고 누락 방지)
DOMAIN_MAP = {"BNAI": "beninc.ai", "AREB": "americanrebel.com", "VEEE": "veea.com", "RVSN": "railvision.io"}

def get_logo_url(ticker):
    domain = DOMAIN_MAP.get(ticker, f"{ticker}.com")
    return f"https://www.google.com/s2/favicons?sz=128&domain={domain}"

# --- UI 메인 ---
st.title("🛡️ Reg sho 등재 목록")

# 티커 검색창
search = st.text_input("🔍 티커 검색", "").upper()

# 3. 데이터 엔진 (문법 오류 수정 및 로직 고정)
def get_verified_data():
    try:
        res = supabase.table("reg_sho_logs").select("symbol, security_name, recorded_date").execute()
        if not res.data: return None
        
        df = pd.DataFrame(res.data)
        df['recorded_date'] = pd.to_datetime(df['recorded_date']).dt.date
        latest_date = df['recorded_date'].max()
        
        # 3/4 이후 실제 추가된 공식 로그 날짜 수 (기존 실증 로직 유지)
        extra_days = len(df[df['recorded_date'] > datetime(2026, 3, 4).date()]['recorded_date'].unique())
        
        current_market = df[df['recorded_date'] == latest_date]
        final_rows = []
        
        for _, row in current_market.iterrows():
            sym, name = row['symbol'], row['security_name'].upper()
            
            # [ETF/Trust 필터] 개별 종목이 아닌 것들은 제외
            if any(kw in name for kw in ["ETF", "TRUST", "FUND", "FD", "TARGET", "DAILY"]):
                continue
            
            # [등재일 산출] PHOTO_FACTS 절대값 기준
            display_days = (PHOTO_FACTS[sym] + extra_days) if sym in PHOTO_FACTS else len(df[df['symbol'] == sym])

            # 🔥 [순서 고정] 등재일 > 로고 > 티커 > 종목명
            final_rows.append({
                "등재일": display_days,
                "로고": get_logo_url(sym),
                "티커": sym,
                "종목명": name
            })
        return pd.DataFrame(final_rows)
    except Exception as e:
        # 문법 오류 방지를 위해 에러 처리 블록을 반드시 포함
        return None

active_df = get_verified_data()

if active_df is not None and not active_df.empty:
    if search:
        active_df = active_df[active_df['티커'].str.contains(search)]
    
    # [UI 출력] 요청하신 컬럼 순서 및 한글 명칭 고정
    st.dataframe(
        active_df.sort_values(by="등재일", ascending=False),
        column_config={
            "등재일": st.column_config.NumberColumn("등재일", format="%d 일", width="small"),
            "로고": st.column_config.ImageColumn("", width="small"),
            "티커": st.column_config.TextColumn("티커"),
            "종목명": st.column_config.TextColumn("종목명")
        },
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("데이터를 동기화 중이거나 등재된 종목이 없습니다.")
