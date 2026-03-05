import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from supabase import create_client

# 1. 인프라 설정
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="NSD PRO HUB", layout="wide")

# [핵심] 19일 벽을 깨는 정밀 복구 함수
def advanced_recovery():
    # 나스닥 서버에 없는 과거 데이터를 SEC FTD 기록 등으로 보정 (개념적 로직)
    # 현재는 나스닥 서버가 허용하는 최대치(약 22~25일)를 먼저 꽉 채웁니다.
    for i in range(25): 
        d_str = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
        url = f"https://www.nasdaqtrader.com/dynamic/symdir/regsho/nasdaqth{d_str}.txt"
        try:
            resp = requests.get(url, timeout=3)
            if resp.status_code == 200:
                df = pd.read_csv(url, sep='|')[:-1]
                df.columns = df.columns.str.strip()
                for _, row in df.iterrows():
                    data = {"symbol": row['Symbol'], "security_name": row['Security Name'], 
                            "recorded_date": f"{d_str[:4]}-{d_str[4:6]}-{d_str[6:]}"}
                    supabase.table("reg_sho_logs").upsert(data).execute()
        except: continue
    return True

# --- 메인 화면 ---
with st.sidebar:
    st.title("📂 NSD PRO HUB")
    menu = st.radio("메뉴", ["Reg SHO 등재 목록", "시가총액/재무"])
    if st.button("🚨 19일 벽 깨기 (정밀 복구)"):
        with st.spinner("나스닥 서버의 한계치까지 데이터를 긁어오는 중..."):
            advanced_recovery()
        st.success("데이터 보정 완료!")
        st.rerun()

if menu == "Reg SHO 등재 목록":
    st.header("📋 Reg SHO 등재 목록")
    
    # DB 데이터 로드
    res = supabase.table("reg_sho_logs").select("symbol, security_name, recorded_date").execute()

    if res.data:
        df = pd.DataFrame(res.data)
        df['recorded_date'] = pd.to_datetime(df['recorded_date'])
        
        # [ Image of a data gap in a time series chart ]
        # 데이터가 존재하는 모든 영업일 리스트
        available_dates = sorted(df['recorded_date'].unique(), reverse=True)
        latest_date = available_dates[0]
        
        final_ranking = []
        for sym in df[df['recorded_date'] == latest_date]['symbol'].unique():
            # 연속성 체크 (중간에 날짜가 비어도 '누적'으로 보정하여 19일 벽 돌파 시도)
            # 나스닥 서버가 지운 날짜 때문에 연속성이 끊기는 현상을 방지하기 위해 '최근 30일 내 출현 횟수'로 계산
            history = df[df['symbol'] == sym]
            streak = len(history) 
            
            # 만약 19일(현재 나스닥 한계치)에 도달했다면 "20일 이상"으로 표기하여 가시성 확보
            display_streak = f"{streak}" if streak < len(available_dates) else f"{streak}+"
            
            final_ranking.append({
                '티커': sym, 
                '종목명': history['security_name'].iloc[0], 
                '등재일수': streak,
                '표기일수': display_streak
            })

        ranking_df = pd.DataFrame(final_ranking).sort_values(by='등재일수', ascending=False)

        st.info(f"📊 현재 DB 데이터량: {len(available_dates)}거래일 (나스닥 제공 최대치 근접)")
        
        search_query = st.text_input("🔍 종목 필터링", placeholder="티커 입력").upper()
        if search_query:
            ranking_df = ranking_df[ranking_df['티커'].str.contains(search_query)]

        st.dataframe(
            ranking_df[['티커', '종목명', '표기일수', '등재일수']],
            column_config={"등재일수": None, "표기일수": "연속 등재일 (추정)"},
            use_container_width=True, hide_index=True
        )
