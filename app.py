import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="나스닥 Reg SHO 트래커", layout="wide")

# 1. 연속 일수 계산 함수 (최근 20거래일 스캔)
def count_consecutive_days(symbol):
    count = 0
    checked_dates = []
    
    # 최근 20일간의 데이터를 뒤져서 연속성 확인
    for i in range(25): # 주말 포함 넉넉히 25일 시도
        target_date = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
        url = f"https://www.nasdaqtrader.com/dynamic/symdir/regsho/nasdaqth{target_date}.txt"
        
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200 and symbol in response.text:
                count += 1
                checked_dates.append(target_date)
            elif response.status_code == 200 and symbol not in response.text:
                # 리스트에 없는 날을 발견하면 거기서 멈춤 (연속성 끊김)
                if count > 0: break 
        except:
            continue
    return count, checked_dates

# 2. 메인 UI
st.title("📊 나스닥 Reg SHO 정밀 스캐너")

symbol = st.text_input("심볼 입력 (예: BNAI)", "").upper()

if symbol:
    with st.spinner(f'{symbol}의 등재 일수를 추적 중입니다...'):
        days, history = count_consecutive_days(symbol)
        
        if days > 0:
            st.error(f"🚨 **{symbol}** 종목은 현재 **{days}일 연속** 등재 상태입니다!")
            st.write(f"최근 등재 확인일: {', '.join(history[:5])} ...")
            
            if days >= 13:
                st.warning("⚠️ 13일 이상 등재되었습니다. 강제 청산(Force-out) 가능성을 확인하세요.")
        else:
            st.success(f"✅ **{symbol}** 종목은 현재 클린한 상태입니다.")

st.divider()

# 3. 오늘 전체 리스트 보기 (기존 기능)
@st.cache_data(ttl=3600)
def fetch_today():
    today = datetime.now().strftime('%Y%m%d')
    url = f"https://www.nasdaqtrader.com/dynamic/symdir/regsho/nasdaqth{today}.txt"
    try:
        df = pd.read_csv(url, sep='|')[:-1]
        df.columns = df.columns.str.strip()
        return df
    except:
        return pd.DataFrame()

st.subheader("📋 오늘자 전체 등재 리스트")
df_today = fetch_today()
if not df_today.empty:
    st.dataframe(df_today[['Symbol', 'Security Name']], use_container_width=True)
else:
    st.info("오늘자 공식 리스트가 아직 업데이트되지 않았습니다.")
