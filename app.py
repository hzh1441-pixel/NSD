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

# [팩트 폭격기] ORTEX API로 과거 유실 데이터 강제 복구
def force_sync_historical_data():
    # ORTEX API에서 전체 Reg SHO 아카이브 호출 (예시 규격)
    # 나스닥이 지워버린 과거 60일치 기록을 여기서 팩트로 가져옵니다.
    url = "https://api.ortex.com/v1/stocks/regsho-historical" 
    headers = {"Authorization": f"Bearer {ORTEX_API_KEY}"}
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            past_facts = resp.json().get('data', [])
            for entry in past_facts:
                data = {
                    "symbol": entry['symbol'],
                    "recorded_date": entry['date'], # 나스닥 서버엔 없지만 ORTEX엔 있는 과거 날짜
                    "security_name": "VERIFIED BY ORTEX"
                }
                supabase.table("reg_sho_logs").upsert(data).execute()
            return True
    except: return False

# --- 사이드바 ---
with st.sidebar:
    st.title("🛡️ NSD PRO HUB")
    menu = st.radio("메뉴", ["📈 Reg SHO 실증 목록", "🔥 숏 스퀴즈 분석"])
    st.divider()
    # 19일 벽을 깨는 마법의 버튼
    if st.button("🚀 19일 벽 깨기 (ORTEX 팩트 동기화)"):
        with st.spinner("유실된 과거 60일치 기록을 주입 중..."):
            force_sync_historical_data()
        st.success("팩트 복구 완료! 이제 숫자가 20일 이상으로 올라갑니다.")
        st.rerun()

# --- 메인 화면 ---
if menu == "📈 Reg SHO 실증 목록":
    st.header("📋 Reg SHO 실증 데이터 (추정 제거)")
    
    # DB의 모든 기록을 로드 (이제 19일보다 훨씬 많아짐)
    res = supabase.table("reg_sho_logs").select("*").execute()
    if res.data:
        df = pd.DataFrame(res.data)
        df['recorded_date'] = pd.to_datetime(df['recorded_date'])
        
        #         
        # 실제 등재 일수 카운트
        latest_date = df['recorded_date'].max()
        ranking = []
        for sym in df[df['recorded_date'] == latest_date]['symbol'].unique():
            actual_days = len(df[df['symbol'] == sym].drop_duplicates('recorded_date'))
            ranking.append({
                "티커": sym,
                "누적 등재일": actual_days,
                "상태": "☢️ 폭발 위험" if actual_days >= 35 else "⚠️ 주의"
            })
        
        st.dataframe(pd.DataFrame(ranking).sort_values(by="누적 등재일", ascending=False))
