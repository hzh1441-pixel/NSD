import streamlit as st
import pandas as pd
from supabase import create_client

# 1. 인프라 설정
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 페이지 설정 (전체 화면 최적화)
st.set_page_config(page_title="NSD PRO: FACT TRACKER", layout="wide")

# 로고 가져오기 함수
def get_logo(ticker):
    return f"https://www.google.com/s2/favicons?sz=64&domain={ticker}.com"

# --- 사이드바: 심플하게 유지 ---
with st.sidebar:
    st.title("🛡️ NSD PRO")
    st.divider()
    st.markdown("### 📊 시스템 상태")
    st.success("실시간 데이터 동기화 중")
    st.info("현재 DB 기록 기반으로 등재일을 산출합니다.")

# --- 메인 화면 ---
st.header("📋 Reg SHO 실증 데이터 추적기")

# 2. 데이터 불러오기
res = supabase.table("reg_sho_logs").select("symbol, security_name, recorded_date").execute()

if res.data:
    df = pd.DataFrame(res.data)
    df['recorded_date'] = pd.to_datetime(df['recorded_date'])
    
    # 시스템 기록 총 일수 파악
    total_system_days = len(df['recorded_date'].unique())
    latest_date = df['recorded_date'].max()
    current_list = df[df['recorded_date'] == latest_date]['symbol'].unique()
    
    final_rows = []
    for sym in current_list:
        # DB 내 순수 누적 일수 계산
        streak = len(df[df['symbol'] == sym])
        name = df[df['symbol'] == sym]['security_name'].iloc[0]
        
        final_rows.append({
            "로고": get_logo(sym),
            "티커": sym,
            "종목명": name,
            "등재일": streak,
            "검증": "✅ 실증" if streak < total_system_days else "⏳ 추적중"
        })
    
    # 랭킹 데이터프레임 생성
    ranking_df = pd.DataFrame(final_rows)
    
    # 기본 정렬: 등재일 높은 순
    ranking_df = ranking_df.sort_values(by="등재일", ascending=False)

    # --- UI 출력 (가장 깔끔했던 버전으로 복구) ---
    st.divider()
    
    # 표 상단 필터 및 정렬 안내
    st.caption("💡 각 열의 제목을 클릭하면 티커순, 등재일순으로 정렬할 수 있습니다.")
    
    st.dataframe(
        ranking_df,
        column_config={
            "로고": st.column_config.ImageColumn(""),
            "티커": st.column_config.TextColumn("티커", width="small"),
            "종목명": st.column_config.TextColumn("종목명", width="medium"),
            "등재일": st.column_config.NumberColumn("누적 등재일 (팩트)", format="%d 일"),
            "검증": st.column_config.TextColumn("상태")
        },
        use_container_width=True,
        hide_index=True
    )

    # 하단 정보 요약
    st.divider()
    st.write(f"현재 시스템 누적 기록: **{total_system_days}일**")
else:
    st.warning("데이터베이스 연결을 확인 중입니다...")
