import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from supabase import create_client

# 1. 수파베이스 연결 설정
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="NSD PRO: Short Squeeze Hub", layout="wide")

# 2. 90일 정밀 동기화 함수 (40일 마지노선 분석용)
def sync_to_db(days_to_fetch=90):
    progress_bar = st.progress(0)
    for i in range(days_to_fetch):
        d = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
        url = f"https://www.nasdaqtrader.com/dynamic/symdir/regsho/nasdaqth{d}.txt"
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                df = pd.read_csv(url, sep='|')[:-1]
                df.columns = df.columns.str.strip()
                for _, row in df.iterrows():
                    data = {
                        "symbol": row['Symbol'],
                        "security_name": row['Security Name'],
                        "recorded_date": f"{d[:4]}-{d[4:6]}-{d[6:]}"
                    }
                    supabase.table("reg_sho_logs").upsert(data).execute()
        except: pass
        progress_bar.progress((i + 1) / days_to_fetch)
    return True

# 3. 메인 화면 구성
st.title("🛡️ NSD PRO: 청산 임박 종목 실시간 랭킹")

with st.sidebar:
    st.header("📊 데이터 제어판")
    if st.button("🔄 90일 정밀 데이터 동기화"):
        with st.spinner("3개월치 데이터를 분석하여 DB를 채우는 중..."):
            sync_to_db(90)
        st.success("데이터 확보 완료!")
    st.divider()
    st.info("40일 마지노선 기준으로 실시간 분석 중입니다.")

# 4. 데이터 불러오기 및 가공
res = supabase.table("reg_sho_logs").select("symbol, security_name, recorded_date").execute()

if res.data:
    df_all = pd.DataFrame(res.data)
    # 종목별 등재 일수 계산 및 내림차순 정렬
    ranking = df_all.groupby(['symbol', 'security_name']).size().reset_index(name='등재일수')
    ranking = ranking.sort_values(by='등재일수', ascending=False).reset_index(drop=True)
    
    # 위험도 상태 분류
    def get_status(days):
        if days >= 40: return "☢️ 최종 마지노선 돌파"
        elif days >= 35: return "🔥 청산 임박 (35일+)"
        elif days >= 13: return "⚠️ 의무 청산 구간"
        else: return "ℹ️ 초기 단계"
    ranking['상태'] = ranking['등재일수'].apply(get_status)

    # 5. 실시간 검색 및 목록 출력
    search_query = st.text_input("🔍 특정 종목 검색 (티커 입력)", placeholder="티커를 입력하면 해당 종목만 필터링됩니다.").upper()
    
    display_df = ranking.copy()
    if search_query:
        display_df = display_df[display_df['symbol'].str.contains(search_query)]

    st.subheader(f"📋 Reg SHO 모니터링 리스트 ({len(display_df)}개 종목)")
    
    # 데이터 표 출력
    st.dataframe(
        display_df,
        column_config={
            "symbol": "티커",
            "security_name": "종목명",
            "등재일수": st.column_config.NumberColumn("연속 등재일수", format="%d 일 🗓️"),
            "상태": "청산 위험도"
        },
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("데이터가 비어 있습니다. 왼쪽 [90일 정밀 데이터 동기화]를 먼저 실행해 주세요.")
