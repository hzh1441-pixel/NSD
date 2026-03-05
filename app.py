import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="나스닥 Reg SHO 스캐너", layout="wide")

# 2. 나스닥 공식 데이터 가져오기
@st.cache_data(ttl=3600)
def fetch_data():
    today = datetime.now().strftime('%Y%m%d')
    url = f"https://www.nasdaqtrader.com/dynamic/symdir/regsho/nasdaqth{today}.txt"
    try:
        df = pd.read_csv(url, sep='|')
        df = df[:-1] # 마지막 요약 행 제거
        df.columns = df.columns.str.strip()
        return df, today
    except:
        return pd.DataFrame(), today

# 3. 화면 구성
st.title("📱 실시간 나스닥 Reg SHO 트래커")
df, date = fetch_data()

if not df.empty:
    st.success(f"최신 데이터 업데이트 완료: {date}")
    symbol = st.text_input("검색할 종목 심볼(예: BNAI)", "").upper()
    
    if symbol:
        res = df[df['Symbol'] == symbol]
        if not res.empty:
            st.error(f"⚠️ {symbol} 종목은 현재 등재 상태입니다.")
            st.table(res)
        else:
            st.info(f"✅ {symbol} 종목은 리스트에 없습니다.")
    
    st.divider()
    st.subheader("📋 현재 전체 등재 명단")
    st.dataframe(df[['Symbol', 'Security Name']], use_container_width=True)
else:
    st.warning("데이터를 불러올 수 없습니다. (미국 휴장일이거나 업데이트 시간 전입니다.)")
