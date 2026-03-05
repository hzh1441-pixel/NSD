import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="NSD REG SHO", layout="wide")
st.title("📊 NSD REG SHO (전체 종목 추적기)")

# 2. 데이터 수집 함수 (캐시 적용으로 속도 향상)
@st.cache_data(ttl=3600)
def get_reg_sho_list(target_date):
    url = f"https://www.nasdaqtrader.com/dynamic/symdir/regsho/nasdaqth{target_date}.txt"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200 and "Symbol" in response.text:
            df = pd.read_csv(url, sep='|')[:-1]
            df.columns = df.columns.str.strip()
            return df
    except:
        pass
    return None

# 3. 전체 종목 등재 일수 계산 로직
@st.cache_data(ttl=3600)
def get_full_list_with_days():
    # 오늘 기준 가장 최신 리스트 찾기
    latest_df = None
    latest_date = ""
    for i in range(7):
        d = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
        latest_df = get_reg_sho_list(d)
        if latest_df is not None:
            latest_date = d
            break
    
    if latest_df is None: return None, None

    # 등재 일수 계산 (최근 20거래일 데이터 활용)
    days_map = {sym: 1 for sym in latest_df['Symbol'].tolist()}
    
    # 과거 데이터를 역순으로 확인하며 일수 누적
    for i in range(1, 20):
        prev_date = (datetime.strptime(latest_date, '%Y%m%d') - timedelta(days=i)).strftime('%Y%m%d')
        prev_df = get_reg_sho_list(prev_date)
        
        if prev_df is not None:
            prev_symbols = set(prev_df['Symbol'].tolist())
            for sym in list(days_map.keys()):
                if sym in prev_symbols:
                    days_map[sym] += 1
                else:
                    # 연속성이 끊긴 종목은 더 이상 계산하지 않음
                    pass 
        else: continue # 주말/휴장일은 건너뜀

    latest_df['Days'] = latest_df['Symbol'].map(days_map)
    return latest_df, latest_date

# 4. 화면 구성
full_df, update_date = get_full_list_with_days()

if full_df is not None:
    st.success(f"✅ {update_date} 데이터 기준 | 총 {len(full_df)}개 종목 분석 완료")
    
    # 상단 요약 지표 (13일 이상 위험 종목 표시)
    danger_count = len(full_df[full_df['Days'] >= 13])
    st.metric("13거래일 이상 등재 (위험)", f"{danger_count} 종목")

    # 정렬 버튼 레이아웃
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        sort_by_name = st.button("🔤 이름순 정렬")
    with col2:
        sort_by_days = st.button("🔥 등재일순 정렬")

    # 데이터 정렬 처리
    display_df = full_df[['Symbol', 'Security Name', 'Days', 'Market Category']]
    if sort_by_name:
        display_df = display_df.sort_values(by='Symbol')
    elif sort_by_days:
        display_df = display_df.sort_values(by='Days', ascending=False)
    else:
        # 기본값은 등재일 높은 순
        display_df = display_df.sort_values(by='Days', ascending=False)

    # 표 출력
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Days": st.column_config.NumberColumn("연속 등재일", format="%d 일 🗓️"),
            "Symbol": "티커",
            "Security Name": "종목명"
        }
    )
else:
    st.error("나스닥 서버에서 데이터를 불러올 수 없습니다.")
