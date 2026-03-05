import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="NSD REG SHO", layout="wide")
st.title("📊 NSD REG SHO (실시간 트래커)")

# 2. 데이터 수집 핵심 함수
def get_reg_sho_list(target_date):
    url = f"https://www.nasdaqtrader.com/dynamic/symdir/regsho/nasdaqth{target_date}.txt"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200 and "Symbol" in response.text:
            df = pd.read_csv(url, sep='|')[:-1] # 마지막 요약줄 제거
            df.columns = df.columns.str.strip()
            return df
    except:
        pass
    return None

# 3. 연속 일수 및 최신 데이터 확인 로직
st.subheader("🔎 종목 정밀 분석")
symbol_input = st.text_input("심볼을 입력하세요 (예: BNAI)", "").upper()

if symbol_input:
    progress_text = st.empty()
    days_count = 0
    found_dates = []
    
    # 최근 30일간을 역순으로 훑으며 '연속성' 계산
    for i in range(30):
        check_date = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
        progress_text.text(f"⏳ {check_date} 나스닥 공식 기록 대조 중...")
        
        df = get_reg_sho_list(check_date)
        
        if df is not None:
            if symbol_input in df['Symbol'].values:
                days_count += 1
                found_dates.append(check_date)
            else:
                # 리스트에 없는 날이 나오면 연속성이 끊긴 것이므로 중단
                if days_count > 0: break
        else:
            # 주말/휴장일로 파일이 없는 경우는 무시하고 계속 진행 (연속성 유지)
            continue
            
    progress_text.empty() # 진행 메시지 삭제

    if days_count > 0:
        st.error(f"### 🚨 {symbol_input} : 현재 {days_count}일 연속 등재 중")
        with st.expander("상세 등재 날짜 보기"):
            st.write(", ".join(found_dates))
        if days_count >= 13:
            st.warning("⚠️ **경고:** 13거래일 이상 연속 등재! 강제 청산 규정 적용 대상일 수 있습니다.")
    else:
        st.success(f"### ✅ {symbol_input} : 현재 리스트에 없습니다.")

st.divider()

# 4. 오늘자(혹은 가장 최신) 전체 명단 출력
st.subheader("📋 전체 등재 명단 확인")
with st.status("최신 전체 리스트를 불러오는 중...", expanded=True) as status:
    latest_df = None
    for i in range(7):
        d = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
        latest_df = get_reg_sho_list(d)
        if latest_df is not None:
            st.write(f"✅ {d} 데이터 확인 완료")
            status.update(label=f"{d} 리스트 로드 완료", state="complete")
            break
    
    if latest_df is not None:
        st.dataframe(latest_df[['Symbol', 'Security Name', 'Market Category']], use_container_width=True)
    else:
        st.error("나스닥 서버에서 데이터를 가져올 수 없습니다. 잠시 후 다시 시도해 주세요.")
