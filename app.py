import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="NSD REG SHO", layout="wide")
st.title("📊 NSD REG SHO")

# 2. 나스닥 서버 데이터 수집 (캐시 적용)
@st.cache_data(ttl=3600)
def get_nasdaq_symbols(date_str):
    url = f"https://www.nasdaqtrader.com/dynamic/symdir/regsho/nasdaqth{date_str}.txt"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200 and "Symbol" in response.text:
            df = pd.read_csv(url, sep='|')[:-1]
            df.columns = [c.strip() for c in df.columns]
            return set(df['Symbol'].unique()), df[['Symbol', 'Security Name']]
    except:
        pass
    return None, None

# 3. 거래일 기준 정밀 분석 로직 (60일 추적)
@st.cache_data(ttl=3600)
def run_full_analysis():
    # 최신 영업일 데이터 찾기
    latest_df = None
    latest_date = None
    for i in range(7):
        d = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
        syms, raw_df = get_nasdaq_symbols(d)
        if syms:
            latest_date = d
            latest_df = raw_df
            break
    
    if latest_df is None: return None, None

    # 등재 일수 계산 시작
    current_symbols = latest_df['Symbol'].unique().tolist()
    days_map = {sym: 1 for sym in current_symbols}
    streak_active = {sym: True for sym in current_symbols}
    
    # 과거 60일간의 데이터를 역순으로 확인
    current_dt = datetime.strptime(latest_date, '%Y%m%d')
    for i in range(1, 60):
        if not any(streak_active.values()): break
        check_date = (current_dt - timedelta(days=i)).strftime('%Y%m%d')
        prev_syms, _ = get_nasdaq_symbols(check_date)
        
        if prev_syms is None: # 주말이나 공휴일 등으로 파일이 없는 경우
            continue # 거래일이 아니므로 연속성을 깨지 않고 건너뜀
        
        # 실제 장이 열린 날(파일이 존재하는 날) 데이터 대조
        for sym in current_symbols:
            if streak_active[sym]:
                if sym in prev_syms:
                    days_map[sym] += 1
                else:
                    streak_active[sym] = False # 리스트에 없으므로 스트릭 종료
                    
    latest_df['연속 등재일'] = latest_df['Symbol'].map(days_map)
    return latest_df, latest_date

# 4. UI 및 기능 구현
with st.spinner('거래일 기준 정밀 데이터를 분석 중입니다...'):
    df, update_date = run_full_analysis()

if df is not None:
    st.info(f"📅 데이터 기준일: {update_date} (나스닥 공식 데이터)")

    # [기능 1] 검색창 (요청하신 대로 '티커'로 변경)
    search_ticker = st.text_input("티커", "").upper()
    
    if search_ticker:
        search_res = df[df['Symbol'] == search_ticker]
        if not search_res.empty:
            days = search_res.iloc[0]['연속 등재일']
            st.error(f"🚨 {search_ticker} : 현재 {days}거래일 연속 등재 중")
            if days >= 13:
                st.warning("⚠️ 13거래일 이상 등재되었습니다. 강제 청산 규정 대상 여부를 확인하십시오.")
        else:
            st.success(f"✅ {search_ticker} : 현재 리스트에 없습니다.")

    st.divider()

    # [기능 2] 정렬 버튼
    col1, col2, _ = st.columns([1, 1, 4])
    with col1:
        sort_by_days = st.button("🔥 등재일 순 정렬")
    with col2:
        sort_by_name = st.button("🔤 이름 순 정렬")

    # 데이터 정렬 처리
    display_df = df[['Symbol', 'Security Name', '연속 등재일']]
    if sort_by_days:
        display_df = display_df.sort_values(by='연속 등재일', ascending=False)
    elif sort_by_name:
        display_df = display_df.sort_values(by='Symbol')
    else:
        display_df = display_df.sort_values(by='연속 등재일', ascending=False) # 기본값

    # [기능 3] 표 출력
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "연속 등재일": st.column_config.NumberColumn("연속 거래일", format="%d일 🗓️"),
            "Symbol": "티커",
            "Security Name": "종목명"
        }
    )
else:
    st.error("데이터 로드 실패. 미국 시차 또는 서버 상태를 확인하세요.")
