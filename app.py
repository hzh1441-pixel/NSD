import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="NSD REG SHO", layout="wide")
st.title("📊 NSD REG SHO (유연한 연속성 모드)")

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
            return "NO_FILE", None
    except:
        pass
    return "SERVER_ERROR", None

# 3. 유연한 연속성 분석 로직 (최대 60거래일 추적)
@st.cache_data(ttl=3600)
def run_flexible_analysis():
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
    missing_streak = {sym: 0 for sym in symbols} # 연속 부재 횟수 기록
    streak_active = {sym: True for sym in symbols}
    
    current_dt = datetime.strptime(latest_date, '%Y%m%d')
    for i in range(1, 60): # 2월 중순까지 충분히 도달하도록 설정
        if not any(streak_active.values()): break
        check_date = (current_dt - timedelta(days=i)).strftime('%Y%m%d')
        prev_syms, _ = fetch_nasdaq_data(check_date)
        
        if prev_syms == "NO_FILE" or prev_syms == "SERVER_ERROR":
            continue # 데이터가 없는 날은 연속성을 유지하며 건너뜀
        
        for sym in symbols:
            if streak_active[sym]:
                if sym in prev_syms:
                    days_map[sym] += 1
                    missing_streak[sym] = 0 # 존재 확인 시 부재 횟수 초기화
                else:
                    missing_streak[sym] += 1
                    # 2거래일 연속으로 명단에 없어야만 확실한 '탈출'로 간주
                    if missing_streak[sym] >= 2:
                        streak_active[sym] = False
                    else:
                        # 1일 부재는 '데이터 오류' 가능성으로 보고 일단 일수 추가
                        days_map[sym] += 1 
                        
    latest_df['연속 거래일'] = latest_df['Symbol'].map(days_map)
    return latest_df, latest_date

# 4. 메인 화면 구성
with st.spinner('데이터 누락을 보정하며 정밀 분석 중입니다...'):
    df, update_date = run_flexible_analysis()

if df is not None:
    st.info(f"📅 데이터 기준일: {update_date} (유연한 연속성 로직 적용됨)")

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
        if st.button("🔥 등재일 순 정렬"):
            st.session_state.sort = "days"
    with col2:
        if st.button("🔤 이름 순 정렬"):
            st.session_state.sort = "name"

    # 정렬 상태 관리
    if 'sort' not in st.session_state: st.session_state.sort = "days"
    
    display_df = df[['Symbol', 'Security Name', '연속 거래일']]
    if st.session_state.sort == "name":
        display_df = display_df.sort_values(by='Symbol')
    else:
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
    st.error("나스닥 서버 연결 실패. 잠시 후 새로고침하세요.")
