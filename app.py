import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

# 1. 페이지 설정 및 디자인 CSS
st.set_page_config(page_title="NSD REG SHO Pro", layout="wide")
st.markdown("""
    <style>
    .metric-card { background-color: #1e2130; padding: 20px; border-radius: 10px; border: 1px solid #3d425a; }
    .stDataFrame { border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# 2. 데이터 수집 (정밀 재시도 로직)
@st.cache_data(ttl=3600)
def fetch_data(date_str):
    url = f"https://www.nasdaqtrader.com/dynamic/symdir/regsho/nasdaqth{date_str}.txt"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200 and "Symbol" in response.text:
            df = pd.read_csv(url, sep='|')[:-1]
            df.columns = df.columns.str.strip()
            return set(df['Symbol'].unique()), df[['Symbol', 'Security Name']]
    except: pass
    return None, None

# 3. 60거래일 전수 조사 로직
@st.cache_data(ttl=3600)
def run_pro_analysis():
    latest_df = None
    latest_date = None
    for i in range(10):
        d = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
        res, data_df = fetch_data(d)
        if isinstance(res, set):
            latest_date, latest_df = d, data_df
            break
    if latest_df is None: return None, None

    symbols = latest_df['Symbol'].unique().tolist()
    days_map = {sym: 1 for sym in symbols}
    missing = {sym: 0 for sym in symbols}
    active = {sym: True for sym in symbols}
    
    # 60거래일 정밀 역추적 (3일 허용 오차)
    curr_dt = datetime.strptime(latest_date, '%Y%m%d')
    found, offset = 1, 1
    while found < 60 and offset < 90:
        c_date = (curr_dt - timedelta(days=offset)).strftime('%Y%m%d')
        prev_syms, _ = fetch_data(c_date)
        offset += 1
        if prev_syms:
            found += 1
            for sym in symbols:
                if active[sym]:
                    if sym in prev_syms:
                        days_map[sym] += 1
                        missing[sym] = 0
                    else:
                        missing[sym] += 1
                        if missing[sym] > 3: active[sym] = False
                        else: days_map[sym] += 1
    
    latest_df['Days'] = latest_df['Symbol'].map(days_map)
    # 신규 종목 판별 (어제 없었던 종목)
    prev_day_date = (curr_dt - timedelta(days=1)).strftime('%Y%m%d')
    yesterday_syms, _ = fetch_data(prev_day_date)
    latest_df['IsNew'] = latest_df['Symbol'].apply(lambda x: yesterday_syms and x not in yesterday_syms if yesterday_syms else False)
    
    return latest_df, latest_date

# 4. 메인 대시보드 UI
df, update_date = run_pro_analysis()

if df is not None:
    st.title("📈 RegSHO 공매도 감시 Pro")
    
    # 상단 메트릭 대시보드
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("등록된 티커", f"{len(df)}", "-1" if "전일대비" else "") # 예시 지표
    with m2: st.metric("위험 티커 (13일+)", len(df[df['Days'] >= 13]))
    with m3: st.metric("주의 티커 (5일+)", len(df[(df['Days'] >= 5) & (df['Days'] < 13)]))
    with m4: st.metric("신규 티커", len(df[df['IsNew'] == True]))

    st.divider()

    # 탭 메뉴 (전문 앱 느낌)
    tab1, tab2, tab3, tab4 = st.tabs(["전체", "고위험(13일+)", "주의(5일+)", "신규"])
    
    search = st.text_input("🔍 티커 검색", "").upper()
    
    def display_tab_data(target_df):
        if search: target_df = target_df[target_df['Symbol'].str.contains(search)]
        st.dataframe(target_df[['Symbol', 'Security Name', 'Days']].sort_values('Days', ascending=False), 
                     use_container_width=True, hide_index=True,
                     column_config={"Days": st.column_config.NumberColumn("연속 등재일", format="%d일 🔥")})

    with tab1: display_tab_data(df)
    with tab2: display_tab_data(df[df['Days'] >= 13])
    with tab3: display_tab_data(df[df['Days'] >= 5])
    with tab4: display_tab_data(df[df['IsNew'] == True])
