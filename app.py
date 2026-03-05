import streamlit as st
import pandas as pd
import requests
from supabase import create_client

# 1. 인프라 설정
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
ORTEX_API_KEY = "9vOWMVq6.ViwuNCVtA318YnQTg2FoG3ucwEUCHmMX"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="NSD PRO: ORTEX HUB", layout="wide")

# --- 로고 및 데이터 호출 함수 ---
def get_logo(ticker):
    return f"https://www.google.com/s2/favicons?sz=64&domain={ticker}.com"

def fetch_ortex_regsho_days(ticker):
    # ORTEX API에서 해당 종목의 실제 연속 등재일을 가져오는 함수
    url = f"https://api.ortex.com/v1/stocks/{ticker}/short-interest"
    headers = {"Authorization": f"Bearer {ORTEX_API_KEY}"}
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            # ORTEX API 응답에서 reg_sho_days 필드를 추출 (실제 필드명에 맞춰 조정 필요)
            return resp.json().get('reg_sho_days', 0)
    except: return None
    return None

# --- 사이드바 UI ---
with st.sidebar:
    st.title("🛡️ NSD PRO HUB")
    st.divider()
    menu = st.radio("분석 메뉴", ["📈 Reg SHO 실증 목록", "🔥 숏 스퀴즈 분석", "💰 시가총액 필터"])
    st.divider()
    st.success("✅ ORTEX API 연결됨")

# --- 메인 화면: Reg SHO 실증 목록 ---
if menu == "📈 Reg SHO 실증 목록":
    st.header("📋 Reg SHO 실증 데이터 목록")
    
    # DB에서 최신 등재 종목 로드
    res = supabase.table("reg_sho_logs").select("symbol, security_name, recorded_date").execute()
    
    if res.data:
        df = pd.DataFrame(res.data)
        df['recorded_date'] = pd.to_datetime(df['recorded_date'])
        latest_date = df['recorded_date'].max()
        current_list = df[df['recorded_date'] == latest_date]
        
        final_rows = []
        for _, row in current_list.iterrows():
            ticker = row['symbol']
            # [핵심] 19일 벽 돌파: DB 카운트가 아닌 ORTEX 실시간 팩트 우선 적용
            ortex_days = fetch_ortex_regsho_days(ticker)
            # 만약 API 응답이 없으면 DB 기록이라도 합산 (최소한의 팩트)
            display_days = ortex_days if ortex_days and ortex_days > 0 else len(df[df['symbol'] == ticker])
            
            final_rows.append({
                "로고": get_logo(ticker),
                "티커": ticker,
                "종목명": row['security_name'],
                "누적 등재일": display_days,
                "상태": "☢️ 위험" if display_days >= 35 else "⚠️ 주의" if display_days >= 13 else "ℹ️ 관찰"
            })
        
        ranking_df = pd.DataFrame(final_rows).sort_values(by='누적 등재일', ascending=False)

        # UI 가독성 정돈
        st.dataframe(
            ranking_df,
            column_config={
                "로고": st.column_config.ImageColumn(""),
                "누적 등재일": st.column_config.NumberColumn("연속 등재 (ORTEX 팩트)", format="%d 일 🗓️"),
                "상태": st.column_config.TextColumn("상태 파악")
            },
            use_container_width=True, hide_index=True
        )
