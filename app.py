import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

# 1. 페이지 및 제목 설정
st.set_page_config(page_title="NSD REG SHO", layout="wide")
st.title("📊 NSD REG SHO (30거래일 정밀 검증)")

# 2. 나스닥 데이터 수집 함수
@st.cache_data(ttl=3600)
def fetch_data(date_str):
    url = f"https://www.nasdaqtrader.com/dynamic/symdir/regsho/nasdaqth{date_str}.txt"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200 and "Symbol" in response.text:
            df = pd.read_csv(url, sep='|')[:-1]
            df.columns = df.columns.str.strip() # 열 이름 공백 제거
            return set(df['Symbol'].unique()), df[['Symbol', 'Security Name']]
        elif response.status_code == 404:
            return "NO_FILE", None
    except:
        pass
    return "ERROR", None

# 3. 30거래일 & 3일 허용 오차 분석 로직
@st.cache_data(ttl=3600)
def run_analysis():
    latest_df = None
    latest_date = None
    # 가장 최근 영업일 데이터 확보
    for i in range(10):
        d = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
        res, data_df = fetch_data(d)
        if isinstance(res, set):
            latest_date = d
            latest_df = data_df
            break
    
    if latest_df is None: return None, None

    symbols = latest_df['Symbol'].unique().tolist()
    days_map = {sym: 1 for sym in symbols}
    missing_streak = {sym: 0 for sym in symbols}
    active_streak = {sym: True for sym in symbols}
    
    current_dt = datetime.strptime(latest_date, '%Y%m%d')
    trading_days_found = 1
    offset = 1

    # 정확히 30거래일을 채울 때까지 과거 역추적
    while trading_days_found < 30 and offset < 60:
        check_date = (current_dt - timedelta(days=offset)).strftime('%Y%m%d')
        prev_syms, _ = fetch_data(check_date)
        offset += 1

        if prev_syms == "NO_FILE" or prev_syms == "ERROR":
            continue # 주말/휴장일/에러는 거래일 카운트 제외
        
        trading_days_found += 1
        for sym in symbols:
            if active_streak[sym]:
                if sym in prev_syms:
                    days_map[sym] += 1
                    missing_streak[sym] = 0
                else:
                    missing_streak[sym] += 1
                    # [핵심] 3일 연속 부재까지는 허용, 4일째에 등재 종료 판정
                    if missing_streak[sym] > 3:
                        active_streak[sym] = False
                    else:
                        days_map[sym] += 1 # 허용 범위 내 부재는 일수 합산
                        
    latest_df['연속 거래일'] = latest_df['Symbol'].map(days_map)
    return latest_df, latest_date

# 4. 메인 화면 UI 구현
with st.spinner('30거래일 데이터를 정밀 분석 중입니다...'):
    df, update_date = run_analysis()

if df is not None:
    st.info(f"📅 기준일: {update_date} | 30거래일 전수 조사 완료")

    # 검색바 (티커)
    search = st.text_input("티커", "").upper()
    if search:
        res = df[df['Symbol'] == search]
        if not res.empty:
            st.error(f"🚨 {search} : 현재 {res.iloc[0]['연속 거래일']}거래일 연속 등재 중")
        else:
            st.success(f"✅ {search} : 현재 리스트에 없습니다.")

    st.divider()

    # 정렬 및 결과 테이블
    col1, col2, _ = st.columns([1, 1, 4])
    with col1:
        sort_days = st.button("🔥 등재일 순")
    with col2:
        sort_name = st.button("🔤 이름 순")

    display_df = df[['Symbol', 'Security Name', '연속 거래일']]
    
    # 정렬 로직
    if sort_name:
        display_df = display_df.sort_values(by='Symbol')
    else:
        display_df = display_df.sort_values(by='연속 거래일', ascending=False)

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={"연속 거래일": st.column_config.NumberColumn(format="%d일 🗓️")}
    )
else:
    st.error("나스닥 서버 연결에 실패했습니다. 잠시 후 새로고침해 주세요.")
