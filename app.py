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

# 로고를 가져오기 위한 유틸리티 함수
def get_logo_url(ticker):
    # Clearbit 무료 API를 활용 (기업 도메인이 아닌 티커로 유추)
    return f"https://logo.clearbit.com/{ticker}.com"

# --- 데이터 수집 및 분석 로직 (이전과 동일) ---
def sync_data(target_date_str):
    url = f"https://www.nasdaqtrader.com/dynamic/symdir/regsho/nasdaqth{target_date_str}.txt"
    try:
        resp = requests.get(url, timeout=5)
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

# --- 사이드바 및 자동 동기화 ---
with st.sidebar:
    st.title("📂 NSD PRO HUB")
    menu = st.radio("메뉴 선택", ["Reg SHO 등재 목록", "주요 공시(SEC)", "시가총액/재무", "설정"])
    if st.button("🔄 90일 기록 강제 복구"):
        with st.spinner("과거 기록 복구 중..."):
            for i in range(90):
                d = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
                sync_data(d)
        st.success("무결성 확보 완료!")

# --- 메인 화면: Reg SHO 등재 목록 ---
if menu == "Reg SHO 등재 목록":
    if "first_run" not in st.session_state:
        for i in range(5):
            target_d = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
            sync_data(target_d)
        st.session_state["first_run"] = True

    st.header("📋 Reg SHO 등재 목록")

    res = supabase.table("reg_sho_logs").select("symbol, security_name, recorded_date").execute()

    if res.data:
        df = pd.DataFrame(res.data)
        df['recorded_date'] = pd.to_datetime(df['recorded_date'])
        
        available_dates = sorted(df['recorded_date'].unique(), reverse=True)
        latest_date = available_dates[0]
        latest_list = df[df['recorded_date'] == latest_date]
        
        final_ranking = []
        for _, row in latest_list.iterrows():
            sym = row['symbol']
            name = row['security_name']
            # 로고 URL 생성
            logo = get_logo_url(sym)
            # 해당 종목의 누적 일수 계산 (연속성 강화 로직)
            streak = len(df[df['symbol'] == sym])
            final_ranking.append({'로고': logo, 'symbol': sym, '종목명': name, '등재일수': streak})

        ranking_df = pd.DataFrame(final_ranking).sort_values(by='등재일수', ascending=False)

        # 40일 마지노선 상태 분류
        def get_status(days):
            if days >= 40: return "☢️ 최종 마지노선"
            elif days >= 35: return "🔥 청산 임박"
            elif days >= 13: return "⚠️ 의무 구간"
            else: return "ℹ️ 초기 단계"
        ranking_df['상태'] = ranking_df['등재일수'].apply(get_status)

        search_query = st.text_input("🔍 종목 필터링", placeholder="티커 입력").upper()
        if search_query:
            ranking_df = ranking_df[ranking_df['symbol'].str.contains(search_query)]

        # 표 출력 (로고 컬럼을 이미지로 렌더링)
        st.dataframe(
            ranking_df,
            column_config={
                "로고": st.column_config.ImageColumn("로고", help="기업 로고"),
                "symbol": "티커",
                "등재일수": st.column_config.NumberColumn("연속 등재일", format="%d 일 🗓️")
            },
            use_container_width=True, hide_index=True
        )
    else:
        st.warning("데이터 동기화 중입니다...")
