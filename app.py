import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="NSD REG SHO", layout="wide")
st.title("📊 NSD REG SHO (30거래일 무결성 검증)")

# 2. 데이터 수집 함수 (나스닥 서버 직접 호출)
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
    return "ERROR", None

# 3. 30거래일 & 3일 허용 오차 분석 로직
@st.cache_data(ttl=3600)
def run_precise_analysis():
    latest_df = None
    latest_date = None
    # 최신 영업일 데이터 확보
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
    missing_streak = {sym: 0 for sym in symbols}
    streak_active = {sym: True for sym in symbols}
    
    current_dt = datetime.strptime(latest_date, '%Y%m%d')
    trading_days_checked = 1
    calendar_offset = 1

    # 정확히 '30거래일'을 채울 때까지 역추적 (최대 50일치 달력 확인)
    while trading_days_checked < 30 and calendar_offset < 50:
        check_date = (current_dt - timedelta(days=calendar_offset)).strftime('%Y%m%d')
        prev_syms, _ = fetch_nasdaq_data(check_date)
        calendar_offset += 1

        if prev_syms == "NO_FILE" or prev_syms == "ERROR":
            continue # 휴장일이나 서버 에러는 거래일 카운트에서 제외
        
        # 실제 거래일 데이터가 존재할 때만 로직 가동
        trading_days_checked += 1
        for sym in symbols:
            if streak_active[sym]:
                if sym in prev_syms:
                    days_map[sym] += 1
                    missing_streak[sym] = 0 # 존재 확인 시 부재 기록 초기화
                else:
                    missing_streak[sym] += 1
                    # [사용자 요청] 3일 연속 부재까지는 허용, 4일째에 종료
                    if missing_streak[sym] > 3:
                        streak_active[sym] = False
                    else:
                        days_map[sym] += 1 # 3일 이내 부재는 데이터 오류로 보정하여 합산

    latest_df['연속 거래일'] = latest_df['Symbol'].map(days_map)
    return latest_df, latest_date

# 4. 화면 구성 (UI)
with st.spinner('최근 30거래일 데이터를 3일 허용 로직으로 분석 중...'):
    df, update_date = run_precise_analysis()

if df is not None:
    st.info(f"📅 기준일: {update_date} | 30거래일 전수 조사 완료")

    # 검색창 (티커)
    search_ticker = st.text_input("티커", "").upper()
    if search_ticker:
        res = df[df['Symbol'] == search_ticker]
        if not res.empty:
            st.error(f"🚨 {search_ticker} : 현재 {res.iloc[0]['연속 거래일']}거래일 연속 등재 중")
        else:
            st.success(f"✅ {search_ticker} : 현재 리스트에 없습니다.")

    st.divider()

    # 정렬 기능
    col1, col2, _ = st.columns([1, 1, 4])
    with col1:
        if st.button("🔥 등재일 순"): st.session_state.sort = "days"
    with col2:
        if st.button("🔤 이름 순"): st.session_state.sort = "name"

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
        column_config={"연속 거래일": st.column_config.NumberColumn(format="%d일 🗓️")}
    )
else:
