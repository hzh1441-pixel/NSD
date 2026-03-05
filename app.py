import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="NSD REG SHO", layout="wide")
st.title("📊 NSD REG SHO")

# 2. 나스닥 서버 데이터 수집 (무결성 로직)
@st.cache_data(ttl=3600)
def fetch_nasdaq_data(date_str):
    url = f"https://www.nasdaqtrader.com/dynamic/symdir/regsho/nasdaqth{date_str}.txt"
    try:
        response = requests.get(url, timeout=7)
        if response.status_code == 200 and "Symbol" in response.text:
            df = pd.read_csv(url, sep='|')[:-1]
            df.columns = [c.strip() for c in df.columns]
            return set(df['Symbol'].unique()), df[['Symbol', 'Security Name']]
        elif response.status_code == 404:
            return "NO_FILE", None # 주말 또는 공휴일
    except:
        pass
    return "SERVER_ERROR", None # 서버 지연 등

# 3. 거래일 기준 정밀 분석 (30거래일 추적)
@st.cache_data(ttl=3600)
def run_analysis():
    # 최신 리스트 확보
    latest_df = None
    latest_date = None
    for i in range(10):
        d = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
        res, data_df = fetch_nasdaq_data(d)
        if isinstance(res, set):
            latest_date = d
            latest_df = data_df
            break
    
    if latest_df is None: return None, None

    symbols = latest_df['Symbol'].unique().tolist()
    days_map = {sym: 1 for sym in symbols}
    streak_active = {sym: True for sym in symbols}
    
    # 과거 거래일 역추적
    current_dt = datetime.strptime(latest_date, '%Y%m%d')
    for i in range(1, 45): # 약 2달치 데이터 확인
        if not any(streak_active.values()): break
        check_date = (current_dt - timedelta(days=i)).strftime('%Y%m%d')
        prev_syms, _ = fetch_nasdaq_data(check_date)
        
        if prev_syms == "NO_FILE" or prev_syms == "SERVER_ERROR":
            continue # 거래일이 아니거나 서버 문제면 연속성 유지
        
        # 실제 데이터가 있는 날에만 비교
        for sym in symbols:
            if streak_active[sym]:
                if sym in prev_syms:
                    days_map[sym] += 1
                else:
                    streak_active[sym] = False # 확실하게 명단에 없는 경우만 중단
                    
    latest_df['연속 거래일'] = latest_df['Symbol'].map(days_map)
    return latest_df, latest_date

# 4. 메인 화면 구성
with st.spinner('거래일 데이터를 정밀 검증 중입니다...'):
    df, update_date = run_analysis()

if df is not None:
    st.info(f"📅 데이터 기준일: {update_date} (나스닥 공식 데이터)")

    # 검색 기능
    search_ticker = st.text_input("티커", "").upper()
    if search_ticker:
        res = df[df['Symbol'] == search_ticker]
        if not res.empty:
            d = res.iloc[0]['연속 거래일']
            st.error(f"🚨 {search_ticker} : 현재 {d}거래일 연속 등재 중")
        else:
            st.success(f"✅ {search_ticker} : 현재 리스트에 없습니다.")

    st.divider()

    # 정렬 기능
    col1, col2, _ = st.columns([1, 1, 4])
    with col1:
        btn_days = st.button("🔥 등재일 순 정렬")
    with col2:
        btn_name = st.button("🔤 이름 순 정렬")

    display_df = df[['Symbol', 'Security Name', '연속 거래일']]
    if btn_name:
        display_df = display_df.sort_values(by='Symbol')
    else:
        # 기본값 및 버튼 클릭 시 등재일 순 정렬
        display_df = display_df.sort_values(by='연속 거래일', ascending=False)

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "연속 거래일": st.column_config.NumberColumn("연속 거래일", format="%d일 🗓️"),
            "Symbol": "티커",
            "Security Name": "종목명"
        }
    )
else:
    st.error("나스닥 서버 연결에 실패했습니다. 잠시 후 새로고침해 주세요.")
