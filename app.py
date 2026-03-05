import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="NSD REG SHO", layout="wide")
st.title("📊 NSD REG SHO")

# 2. 개별 날짜의 데이터를 가져오는 함수
@st.cache_data(ttl=3600)
def get_data_for_date(target_date):
    url = f"https://www.nasdaqtrader.com/dynamic/symdir/regsho/nasdaqth{target_date}.txt"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200 and "Symbol" in response.text:
            df = pd.read_csv(url, sep='|')[:-1]
            df.columns = df.columns.str.strip()
            return set(df['Symbol'].tolist()) # 검색 속도를 위해 세트(set)로 반환
    except:
        pass
    return None

# 3. 연속 등재 일수를 계산하는 핵심 로직
def calculate_consecutive_days(symbol):
    count = 0
    current_date = datetime.now()
    found_any = False
    
    # 최근 30일간의 데이터를 역순으로 확인
    for i in range(30):
        check_date = (current_date - timedelta(days=i)).strftime('%Y%m%d')
        symbols_on_list = get_data_for_date(check_date)
        
        if symbols_on_list is not None:
            if symbol in symbols_on_list:
                count += 1
                found_any = True
            else:
                # 리스트에 없는 날이 발견되면 카운트 중단 (연속성 끊김)
                if found_any: break
        else:
            # 주말이나 휴장일로 데이터가 없는 경우는 건너뜀 (연속성 유지)
            continue
            
    return count

# 4. 화면 구성 (검색 및 결과)
symbol_input = st.text_input("🔍 종목 심볼 입력 (예: BNAI, SMCI)", "").upper()

if symbol_input:
    with st.spinner(f'{symbol_input}의 등재 일수를 나스닥 공식 기록에서 대조 중...'):
        days = calculate_consecutive_days(symbol_input)
        
        if days > 0:
            st.error(f"### 🚨 {symbol_input} : 현재 {days}일 연속 등재 중")
            if days >= 13:
                st.warning("⚠️ **주의:** 13거래일 이상 등재되었습니다. 규정에 따른 강제 청산(Rule 203(b)(3)) 대상인지 확인이 필요합니다.")
        else:
            st.success(f"### ✅ {symbol_input} : 현재 리스트에 없습니다.")

st.divider()

# 5. 오늘자 전체 명단 표시 (참고용)
st.subheader("📋 오늘자 전체 등재 리스트 확인")
today_str = datetime.now().strftime('%Y%m%d')
today_list = get_data_for_date(today_str)

if today_list:
    st.write(f"오늘({today_str}) 등재된 총 종목 수: {len(today_list)}개")
    st.write(", ".join(sorted(list(today_list))))
else:
    st.info("오늘자 공식 리스트가 아직 업데이트되지 않았거나 휴장일입니다. (어제 데이터를 기준으로 검색해 보세요.)")

st.caption("제공되는 정보는 나스닥 공식 TXT 데이터를 기반으로 계산된 객관적 수치입니다.")
