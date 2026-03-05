import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="나스닥 Reg SHO 스캐너", layout="wide")

# 2. 가장 최신 데이터 찾아오기 (오늘부터 3일 전까지 자동 검색)
@st.cache_data(ttl=3600)
def fetch_data():
    for i in range(4): # 오늘(0)부터 3일 전까지 시도
        target_date = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
        url = f"https://www.nasdaqtrader.com/dynamic/symdir/regsho/nasdaqth{target_date}.txt"
        try:
            response = requests.get(url)
            if response.status_code == 200 and "Symbol" in response.text:
                df = pd.read_csv(url, sep='|')
                df = df[:-1] 
                df.columns = df.columns.str.strip()
                return df, target_date
        except:
            continue
    return pd.DataFrame(), "데이터 없음"

# 3. 화면 구성
st.title("📱 실시간 나스닥 Reg SHO 트래커")
df, date = fetch_data()

if not df.empty:
    st.success(f"✅ 최신 확인된 데이터 날짜: {date} (미국 시간 기준)")
    symbol = st.text_input("검색할 종목 심볼(예: BNAI)", "").upper()
    
    if symbol:
        res = df[df['Symbol'] == symbol]
        if not res.empty:
            st.error(f"🚨 {symbol} 종목은 현재 등재 상태입니다!")
            st.table(res)
        else:
            st.info(f"✅ {symbol} 종목은 현재 리스트에 없습니다.")
    
    st.divider()
    st.subheader(f"📋 전체 등재 명단 ({len(df)}개 종목)")
    st.dataframe(df[['Symbol', 'Security Name', 'Market Category']], use_container_width=True)
else:
    st.warning("현재 나스닥 데이터를 불러올 수 없습니다. 장 개설 전이거나 서버 점검 중일 수 있습니다.")
