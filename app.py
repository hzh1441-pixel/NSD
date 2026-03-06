import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from supabase import create_client

# ==========================================
# 1. 기초 설정 및 팩트 데이터
# ==========================================
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"

# 실제 등재일 데이터 (추가하고 싶은 종목은 여기에 추가하세요)
PHOTO_FACTS = {
    "AREB": 27, "VEEE": 25, "ELPW": 21, "SVRN": 20, "CISS": 19, "RVSN": 16,
    "HOOX": 15, "PBOG": 14, "SMX": 13, "UOKA": 13, "BNAI": 12, "MYCH": 12,
    "GFAI": 11, "BRTX": 10, "NCI": 10, "HUBC": 10, "DTST": 10, "HBR": 9,
    "NVDL": 9, "RIME": 9, "SOND": 9, "LFS": 8, "LGHL": 8, "PDC": 8, "KODK": 8,
    "XTKG": 7, "CDIO": 6, "GGLS": 5, "GV": 5, "MGRX": 5, "PFSA": 5, "RUBI": 5,
    "BHAT": 4, "DUOG": 3, "FFAI": 3, "AMZD": 2, "APPX": 2, "IONZ": 2,
    "WHLR": 2
}

st.set_page_config(page_title="NSD PRO", layout="wide")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================
# 2. 데이터 엔진 (보안 및 문법 오류 완벽 수정)
# ==========================================
@st.cache_data(ttl=86400)
def get_sec_names():
    """SEC 서버에서 공식 기업명 명단을 가져옵니다."""
    try:
        headers = {'User-Agent': 'NSD_PRO_Admin contact@nsdpro.com'}
        url = "https://www.sec.gov/files/company_tickers.json"
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            return {item['ticker']: item['title'] for item in data.values()}
    except Exception:
        pass
    return {}

def fetch_verified_data():
    """DB 도장과 명단을 합쳐 최종 등재일을 계산합니다."""
    try:
        # 공식 이름표 가져오기
        sec_names = get_sec_names()
        
        # DB에서 3월 4일 이후의 모든 등재 도장 가져오기
        res = supabase.table("reg_sho_logs").select("symbol, recorded_date").gt("recorded_date", "2026-03-04").execute()
        db_df = pd.DataFrame(res.data) if res.data else pd.DataFrame()
        
        rows = []
        processed_tickers = set()
        
        # 1. VIP 명단(PHOTO_FACTS) 처리
        for ticker, base_day in PHOTO_FACTS.items():
            bonus_day = 0
            if not db_df.empty and 'symbol' in db_df.columns:
                # 해당 티커로 찍힌 고유한 날짜 수 계산
                bonus_day = len(db_df[db_df['symbol'] == ticker]['recorded_date'].unique())
            
            rows.append({
                "등재일": base_day + bonus_day,
                "로고": f"https://www.google.com/s2/favicons?sz=128&domain={ticker}.com",
                "티커": ticker,
                "종목명": sec_names.get(ticker, ticker)
            })
            processed_tickers.add(ticker)
            
        # 2. 사냥개가 새로 물어온 신규 종목 처리 (VIP 명단에 없는 것)
        if not db_df.empty and 'symbol' in db_df.columns:
            new_tickers = db_df[~db_df['symbol'].isin(processed_tickers)]['symbol'].unique()
            for ticker in new_tickers:
                bonus_day = len(db_df[db_df['symbol'] == ticker]['recorded_date'].unique())
                rows.append({
                    "등재일": bonus_day,
                    "로고": f"https://www.google.com/s2/favicons?sz=128&domain={ticker}.com",
                    "티커": ticker,
                    "종목명": sec_names.get(ticker, ticker)
                })
                
        return pd.DataFrame(rows)
    except Exception as e:
        st.error(f"데이터 엔진 실행 중 오류 발생: {e}")
        return pd.DataFrame()

# ==========================================
# 3. 화면 렌더링 (메인 UI)
# ==========================================
st.title("승현쓰껄~ㅋ")

# 데이터 로드
final_df = fetch_verified_data()

if not final_df.empty:
    # 등재일 내림차순 정렬
    sorted_df = final_df.sort_values(by="등재일", ascending=False)
    
    st.dataframe(
        sorted_df,
        column_order=["등재일", "로고", "티커", "종목명"],
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
    st.info("데이터를 불러오는 중이거나 표시할 종목이 없습니다.")
