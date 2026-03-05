import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="NSD REG SHO", layout="wide")
st.title("📊 NSD REG SHO (거래일 정밀 계산기)")

@st.cache_data(ttl=3600)
def fetch_nasdaq_file(date_str):
    url = f"https://www.nasdaqtrader.com/dynamic/symdir/regsho/nasdaqth{date_str}.txt"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200 and "Symbol" in resp.text:
            df = pd.read_csv(url, sep='|')[:-1]
            df.columns = [c.strip() for c in df.columns]
            return set(df['Symbol'].unique())
        return "EMPTY" # 파일이 없음 (주말/휴일)
    except:
        return "ERROR" # 서버 통신 에러

def get_accurate_analysis():
    # 1. 최신 영업일 파일 찾기
    latest_df = None
    latest_date = None
    for i in range(10):
        d = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
        data = fetch_nasdaq_file(d)
        if isinstance(data, set):
            latest_date = d
            # 표시용 전체 데이터 로드
            raw_url = f"https://www.nasdaqtrader.com/dynamic/symdir/regsho/nasdaqth{d}.txt"
            latest_df = pd.read_csv(raw_url, sep='|')[:-1]
            latest_df.columns = [c.strip() for c in latest_df.columns]
            break
    
    if not latest_df is not None: return None, None

    # 2. 거래일 기준 역추적 (최대 60일)
    symbols = latest_df['Symbol'].unique().tolist()
    days_map = {sym: 1 for sym in symbols}
    active_streak = {sym: True for sym in symbols}
    
    current_check = datetime.strptime(latest_date, '%Y%m%d')
    trading_days_found = 1
    
    # 과거로 60일간의 '거래일'을 뒤짐
    for i in range(1, 80): 
        if trading_days_found >= 60: break
        check_date = (current_check - timedelta(days=i)).strftime('%Y%m%d')
        prev_symbols = fetch_nasdaq_file(check_date)
        
        if isinstance(prev_symbols, set): # 정상 거래일 데이터 발견
            trading_days_found += 1
            for sym in symbols:
                if active_streak[sym]:
                    if sym in prev_symbols:
                        days_map[sym] += 1
                    else:
                        active_streak[sym] = False # 리스트에 없으므로 스트릭 종료
        elif prev_symbols == "EMPTY":
            continue # 휴장일이므로 카운트 유지하고 다음 날짜 확인
        else:
            continue # 서버 에러일 경우 일단 유지하고 더 과거 확인
            
    latest_df['연속 거래일'] = latest_df['Symbol'].map(days_map)
    return latest_df, latest_date

# 실행 및 결과 출력
with st.spinner('나스닥 공식 서버에서 거래일 데이터를 정밀 대조 중입니다...'):
    df, last_date = get_accurate_analysis()

if df is not None:
    st.success(f"✅ {last_date} 기준 데이터 (주말/공휴일 제외 거래일 계산 완료)")
    
    # 13일 이상 종목 하이라이트
    danger_df = df[df['연속 거래일'] >= 13]
    if not danger_df.empty:
        st.warning(f"⚠️ 현재 13거래일 이상 등재된 종목이 {len(danger_df)}개 있습니다.")

    # 표 출력
    display_df = df[['Symbol', 'Security Name', '연속 거래일']].sort_values(by='연속 거래일', ascending=False)
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={"연속 거래일": st.column_config.NumberColumn("연속 거래일", format="%d일 🔥")}
    )
else:
    st.error("데이터를 불러오는 데 실패했습니다. 잠시 후 새로고침해 보세요.")
