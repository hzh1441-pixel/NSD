import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="NSD REG SHO", layout="wide")
st.title("📊 NSD REG SHO (전체 종목 추적기)")

# 2. 데이터 수집 함수 (오류 방지 로직 강화)
@st.cache_data(ttl=3600)
def get_reg_sho_list(target_date):
    url = f"https://www.nasdaqtrader.com/dynamic/symdir/regsho/nasdaqth{target_date}.txt"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200 and "Symbol" in response.text:
            df = pd.read_csv(url, sep='|')
            df = df[:-1] # 마지막 요약 행 제거
            # 열 이름의 앞뒤 공백을 강제로 제거하여 'Symbol'을 확실히 찾게 함
            df.columns = [c.strip() for c in df.columns]
            return df
    except:
        pass
    return None

# 3. 전체 종목의 등재 일수 계산
@st.cache_data(ttl=3600)
def get_full_analysis():
    latest_df = None
    latest_date = ""
    # 최신 리스트 찾기
    for i in range(7):
        d = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
        latest_df = get_reg_sho_list(d)
        if latest_df is not None and 'Symbol' in latest_df.columns:
            latest_date = d
            break
    
    if latest_df is None: return None, None

    # 등재 일수 계산 시작
    symbols = latest_df['Symbol'].unique().tolist()
    days_map = {sym: 1 for sym in symbols}
    
    # 과거 20거래일 데이터 대조
    for i in range(1, 20):
        prev_date = (datetime.strptime(latest_date, '%Y%m%d') - timedelta(days=i)).strftime('%Y%m%d')
        prev_df = get_reg_sho_list(prev_date)
        
        if prev_df is not None and 'Symbol' in prev_df.columns:
            prev_symbols = set(prev_df['Symbol'].tolist())
            for sym in list(days_map.keys()):
                if sym in prev_symbols:
                    days_map[sym] += 1
                else:
                    # 연속성이 끊기면 해당 종목 계산 중단
                    pass 
        else: continue 

    latest_df['연속 등재일'] = latest_df['Symbol'].map(days_map)
    return latest_df, latest_date

# 4. 화면 구성
with st.spinner('나스닥 공식 데이터를 분석 중입니다...'):
    df, update_date = get_full_analysis()

if df is not None:
    st.success(f"✅ {update_date} 데이터 기준 분석 완료")

    # 정렬 및 검색 옵션
    col1, col2, col3 = st.columns([1.5, 1.5, 4])
    with col1:
        sort_type = st.radio("정렬 기준", ["등재일 많은 순", "티커(이름) 순"], horizontal=True)
    
    # 데이터 정리
    display_df = df[['Symbol', 'Security Name', '연속 등재일', 'Market Category']]
    
    if sort_type == "등재일 많은 순":
        display_df = display_df.sort_values(by='연속 등재일', ascending=False)
    else:
        display_df = display_df.sort_values(by='Symbol')

    # 표 출력
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "연속 등재일": st.column_config.NumberColumn("연속 등재일", format="%d 일 🗓️"),
            "Symbol": "티커",
            "Security Name": "종목명",
            "Market Category": "시장 구분"
        }
    )
else:
    st.error("현재 나스닥 데이터를 불러올 수 없습니다. 시차로 인해 업데이트 중일 수 있으니 잠시 후 다시 시도해 주세요.")
