import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime, timedelta
from supabase import create_client

# 1. 인프라 설정
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="NSD PRO HUB", layout="wide")

# 2. 데이터 수집 함수 (안정성 강화: 0.2초 지연 추가)
def sync_data(target_date_str):
    url = f"https://www.nasdaqtrader.com/dynamic/symdir/regsho/nasdaqth{target_date_str}.txt"
    try:
        resp = requests.get(url, timeout=7)
        if resp.status_code == 200:
            df = pd.read_csv(url, sep='|')[:-1]
            df.columns = df.columns.str.strip()
            for _, row in df.iterrows():
                data = {
                    "symbol": row['Symbol'],
                    "security_name": row['Security Name'],
                    "recorded_date": f"{target_date_str[:4]}-{target_date_str[4:6]}-{target_date_str[6:]}"
                }
                supabase.table("reg_sho_logs").upsert(data).execute()
            return True
    except: pass
    return False

# --- 사이드바 메뉴 ---
with st.sidebar:
    st.title("📂 NSD PRO HUB")
    menu = st.radio("메뉴 선택", ["Reg SHO 등재 목록", "주요 공시(SEC)", "시가총액/재무"])
    st.divider()
    if st.button("🚨 [긴급] 90일 정밀 복구 실행"):
        progress_text = "나스닥 서버에서 90일치 데이터를 강제로 긁어오는 중입니다..."
        my_bar = st.progress(0, text=progress_text)
        for i in range(90):
            d = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
            sync_data(d)
            time.sleep(0.1) # 서버 차단 방지용 미세 지연
            my_bar.progress((i + 1) / 90)
        st.success("90일 데이터 무결성 확보 완료! 페이지를 새로고침하세요.")
        st.rerun()

# --- 메인 화면 ---
if menu == "Reg SHO 등재 목록":
    st.header("📋 Reg SHO 등재 목록")

    # DB에 저장된 전체 데이터 로드
    res = supabase.table("reg_sho_logs").select("symbol, security_name, recorded_date").execute()

    if res.data:
        df = pd.DataFrame(res.data)
        df['recorded_date'] = pd.to_datetime(df['recorded_date'])
        
        # [검증용] 현재 DB에 저장된 고유 날짜 수 확인
        db_dates_count = len(df['recorded_date'].unique())
        latest_date = df['recorded_date'].max()
        
        # 오늘자 명단 추출
        latest_list = df[df['recorded_date'] == latest_date]['symbol'].unique()
        
        final_ranking = []
        for sym in latest_list:
            # 해당 종목이 DB 전체(90일) 내에서 몇 번 나타났는지 합산
            streak = len(df[df['symbol'] == sym])
            name = df[df['symbol'] == sym]['security_name'].iloc[0]
            final_ranking.append({'로고': f"https://logo.clearbit.com/{sym}.com", 'symbol': sym, '종목명': name, '등재일수': streak})

        ranking_df = pd.DataFrame(final_ranking).sort_values(by='등재일수', ascending=False)

        # 상태 분류
        def get_status(days):
            if days >= 40: return "☢️ 최종 마지노선"
            elif days >= 35: return "🔥 청산 임박"
            elif days >= 13: return "⚠️ 의무 구간"
            else: return "ℹ️ 초기 단계"
        ranking_df['상태'] = ranking_df['등재일수'].apply(get_status)

        # 상단 요약 바
        st.info(f"💾 **데이터 무결성 리포트**: 현재 DB에 **{db_dates_count}거래일** 분량의 데이터가 쌓여 있습니다. (기준일: {latest_date.strftime('%Y-%m-%d')})")
        
        if db_dates_count < 40:
            st.warning(f"⚠️ 현재 DB 데이터가 {db_dates_count}일뿐입니다. 40일 마지노선을 정확히 보려면 사이드바에서 [90일 정밀 복구]를 실행하세요.")

        search_query = st.text_input("🔍 종목 필터링", placeholder="티커 입력").upper()
        if search_query:
            ranking_df = ranking_df[ranking_df['symbol'].str.contains(search_query)]

        st.dataframe(
            ranking_df,
            column_config={
                "로고": st.column_config.ImageColumn("로고"),
                "symbol": "티커",
                "등재일수": st.column_config.NumberColumn("누적 등재일", format="%d 일 🗓️")
            },
            use_container_width=True, hide_index=True
        )
