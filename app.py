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

# 2. 데이터 수집 함수 (안정성 강화)
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
    if st.button("🚨 [데이터 복구] 과거 90일 정밀 스캔"):
        progress_bar = st.progress(0)
        for i in range(90):
            d = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
            sync_data(d)
            time.sleep(0.05)
            progress_bar.progress((i + 1) / 90)
        st.success("90일치 데이터 무결성 확보 완료!")
        st.rerun()

# --- 메인 화면: Reg SHO 등재 목록 ---
if menu == "Reg SHO 등재 목록":
    st.header("📋 Reg SHO 등재 목록")

    # DB에서 전체 데이터 로드
    res = supabase.table("reg_sho_logs").select("symbol, security_name, recorded_date").execute()

    if res.data:
        df = pd.DataFrame(res.data)
        df['recorded_date'] = pd.to_datetime(df['recorded_date'])
        
        # 현재 DB 내 유효 거래일 확인
        db_dates = sorted(df['recorded_date'].unique(), reverse=True)
        db_dates_count = len(db_dates)
        latest_date = db_dates[0]
        
        # 최신 등재 종목 추출
        latest_list = df[df['recorded_date'] == latest_date]
        
        final_ranking = []
        for _, row in latest_list.iterrows():
            sym = row['symbol']
            # 해당 종목의 누적 일수 계산 (연속성 강화)
            streak = len(df[df['symbol'] == sym])
            final_ranking.append({
                '티커': sym, 
                '종목명': row['security_name'], 
                '등재일수': streak
            })

        ranking_df = pd.DataFrame(final_ranking).sort_values(by='등재일수', ascending=False)

        # 40일 마지노선 상태 분류
        def get_status(days):
            if days >= 40: return "☢️ 최종 마지노선 돌파"
            elif days >= 35: return "🔥 청산 임박 (35일+)"
            elif days >= 13: return "⚠️ 의무 구간"
            else: return "ℹ️ 초기 단계"
        ranking_df['상태'] = ranking_df['등재일수'].apply(get_status)

        # 무결성 리포트 (중요)
        st.info(f"📊 **데이터 무결성 보고**: 현재 DB에 **{db_dates_count}거래일** 분량의 팩트가 쌓여 있습니다.")
        if db_dates_count < 40:
            st.warning(f"⚠️ 현재 확보된 데이터가 {db_dates_count}일뿐입니다. 19일에 멈춘 종목들은 더 과거 데이터가 필요하다는 뜻입니다. 왼쪽 [데이터 복구] 버튼을 눌러주세요.")

        # 검색창
        search_query = st.text_input("🔍 종목 필터링 (티커 입력)", placeholder="찾으시는 티커를 입력하세요.").upper()
        if search_query:
            ranking_df = ranking_df[ranking_df['티커'].str.contains(search_query)]

        # 결과 표 출력 (로고 삭제로 더 넓고 깔끔해진 화면)
        st.dataframe(
            ranking_df,
            column_config={
                "등재일수": st.column_config.NumberColumn("누적 등재일", format="%d 일 🗓️"),
                "상태": "위험도 상태"
            },
            use_container_width=True, hide_index=True
        )
    else:
        st.warning("데이터 동기화 중입니다. 사이드바에서 [데이터 복구]를 실행해 주세요.")
