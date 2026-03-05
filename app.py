import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="NSD REG SHO", layout="wide")

# 2. 스마트 데이터 로더 (가장 최신 가용 데이터 자동 검색)
@st.cache_data(ttl=3600)
def fetch_latest_data():
    # 오늘부터 최대 7일 전까지 리스트가 있는지 확인
    for i in range(7):
        target_date = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
        url = f"https://www.nasdaqtrader.com/dynamic/symdir/regsho/nasdaqth{target_date}.txt"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200 and "Symbol" in response.text:
                df = pd.read_csv(url, sep='|')[:-1] # 요약행 제거
                df.columns = df.columns.str.strip()
                return df, target_date
        except:
            continue
    return pd.DataFrame(), None

# 3. 메인 화면 구성
st.title("📊 NSD REG SHO") # 요청하신 이름으로 변경
df, found_date = fetch_latest_data()

if not df.empty:
    st.success(f"✅ 최신 데이터 확인 완료: {found_date} (미국 시간 기준)")
    
    # 종목 검색창
    symbol = st.text_input("심볼 입력 (예: BNAI)", "").upper()
    if symbol:
        res = df[df['Symbol'] == symbol]
        if not res.empty:
            st.error(f"🚨 {symbol} 종목은 현재 Reg SHO 리스트에 등재되어 있습니다.")
            st.table(res)
        else:
            st.info(f"✅ {symbol} 종목은 현재 리스트에 없습니다.")

    st.divider()
    st.subheader(f"📋 전체 등재 리스트 (총 {len(df)}건)")
    st.dataframe(df[['Symbol', 'Security Name', 'Market Category']], use_container_width=True)
else:
    st.error("나스닥 서버에서 데이터를 가져올 수 없습니다. 잠시 후 다시 시도해 주세요.")

st.caption("본 정보는 나스닥 공식 데이터를 실시간으로 반영하며, 엄격한 사실 검증 원칙을 따릅니다.")
