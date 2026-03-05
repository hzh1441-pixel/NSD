import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="NSD REG SHO", layout="wide")
st.title("📊 NSD REG SHO (정밀 분석 모드)")

@st.cache_data(ttl=3600)
def get_reg_sho_list(target_date):
    url = f"https://www.nasdaqtrader.com/dynamic/symdir/regsho/nasdaqth{target_date}.txt"
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200 and "Symbol" in response.text:
            df = pd.read_csv(url, sep='|')[:-1]
            df.columns = [c.strip() for c in df.columns]
            return set(df['Symbol'].unique()) # 속도를 위해 세트로 반환
    except:
        pass
    return None

@st.cache_data(ttl=3600)
def get_full_analysis():
    latest_df = None
    latest_date = ""
    # 1. 최신 리스트 확보
    for i in range(7):
        d = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
        url = f"https://www.nasdaqtrader.com/dynamic/symdir/regsho/nasdaqth{d}.txt"
        try:
            res = requests.get(url, timeout=3)
            if res.status_code == 200:
                latest_df = pd.read_csv(url, sep='|')[:-1]
                latest_df.columns = [c.strip() for c in latest_df.columns]
                latest_date = d
                break
        except: continue
    
    if latest_df is None: return None, None

    # 2. 정밀 연속 일수 계산 (60일 역추적)
    active_symbols = latest_df['Symbol'].unique().tolist()
    days_map = {sym: 1 for sym in active_symbols}
    still_on_streak = {sym: True for sym in active_symbols}

    # 과거 60일치를 대조하여 연속성 확인
    for i in range(1, 60):
        if not any(still_on_streak.values()): break # 모든 종목 스트릭 깨지면 중단
        
        check_date = (datetime.strptime(latest_date, '%Y%m%d') - timedelta(days=i)).strftime('%Y%m%d')
        prev_symbols = get_reg_sho_list(check_date)
        
        if prev_symbols is not None: # 영업일 데이터가 있는 경우
            for sym in active_symbols:
                if still_on_streak[sym]:
                    if sym in prev_symbols:
                        days_map[sym] += 1
                    else:
                        still_on_streak[sym] = False # 여기서 스트릭 종료
        else:
            continue # 주말/휴일은 건너뛰고 연속성 유지

    latest_df['연속 등재일'] = latest_df['Symbol'].map(days_map)
    return latest_df, latest_date

# 화면 출력
with st.status("나스닥 60일치 공식 기록 정밀 대조 중...", expanded=True) as status:
    df, update_date = get_full_analysis()
    if df is not None:
        status.update(label=f"✅ {update_date} 데이터 분석 완료", state="complete")

if df is not None:
    # 정렬 옵션
    sort_option = st.radio("정렬 방식 선택", ["등재일 많은 순 (위험군)", "티커 이름 순"], horizontal=True)
    
    display_df = df[['Symbol', 'Security Name', '연속 등재일']]
    if sort_option == "등재일 많은 순 (위험군)":
        display_df = display_df.sort_values(by='연속 등재일', ascending=False)
    else:
        display_df = display_df.sort_values(by='Symbol')

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "연속 등재일": st.column_config.NumberColumn("연속 등재일", format="%d 일 🔥"),
            "Symbol": "티커",
            "Security Name": "종목명"
        }
    )
else:
    st.error("데이터 로드 실패. 미국 시차를 확인해 주세요.")
