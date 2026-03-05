import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from supabase import create_client

# 1. 인프라 설정
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="NSD PRO HUB", layout="wide")

# --- [해결사] 과거 데이터 강제 주입 기능 ---
def inject_historical_data(file):
    df_upload = pd.read_csv(file)
    # 파일에는 symbol, security_name, recorded_date가 있어야 함
    for _, row in df_upload.iterrows():
        data = {
            "symbol": row['symbol'],
            "security_name": row['security_name'],
            "recorded_date": row['recorded_date'] # 형식: YYYY-MM-DD
        }
        supabase.table("reg_sho_logs").upsert(data).execute()
    return True

# --- 사이드바: 데이터 관리 ---
with st.sidebar:
    st.title("📂 NSD PRO HUB")
    menu = st.radio("메뉴", ["Reg SHO 등재 목록", "과거 기록 복구", "시가총액/재무"])
    
    if menu == "과거 기록 복구":
        st.subheader("⚠️ 19일 벽 깨기 전용")
        uploaded_file = st.file_uploader("과거 Reg SHO CSV 파일 업로드", type="csv")
        if uploaded_file and st.button("🚀 데이터 강제 주입"):
            inject_historical_data(uploaded_file)
            st.success("과거 기록이 DB에 박제되었습니다! 이제 일수가 정상 출력됩니다.")

# --- 메인 화면: Reg SHO 등재 목록 ---
if menu == "Reg SHO 등재 목록":
    st.header("📋 Reg SHO 등재 목록")
    
    res = supabase.table("reg_sho_logs").select("symbol, security_name, recorded_date").execute()

    if res.data:
        df = pd.DataFrame(res.data)
        df['recorded_date'] = pd.to_datetime(df['recorded_date'])
        
        # 무결성 검증: 존재하는 모든 날짜 정렬
        available_dates = sorted(df['recorded_date'].unique(), reverse=True)
        latest_date = available_dates[0]
        
        final_ranking = []
        for sym in df[df['recorded_date'] == latest_date]['symbol'].unique():
            # 연속성 체크: 추정이 아닌 '실제 DB 기록'만 카운트
            sym_dates = set(df[df['symbol'] == sym]['recorded_date'])
            streak = 0
            for d in available_dates:
                if d in sym_dates: streak += 1
                else: break
            
            name = df[df['symbol'] == sym]['security_name'].iloc[0]
            final_ranking.append({'티커': sym, '종목명': name, '등재일수': streak})

        ranking_df = pd.DataFrame(final_ranking).sort_values(by='등재일수', ascending=False)

        st.info(f"💾 **무결성 팩트 체크**: 현재 DB 내 {len(available_dates)}거래일 기록 확인 중")

        search_query = st.text_input("🔍 종목 필터링", placeholder="티커 입력").upper()
        if search_query:
            ranking_df = ranking_df[ranking_df['티커'].str.contains(search_query)]

        st.dataframe(ranking_df, use_container_width=True, hide_index=True)
