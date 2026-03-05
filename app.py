import streamlit as st
import pandas as pd
import requests
import yfinance as yf
from datetime import datetime, timedelta
import concurrent.futures

# 1. 페이지 설정 및 테마
st.set_page_config(page_title="NSD REG SHO Pro", layout="wide")
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; color: #ff4b4b; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #262730; border-radius: 5px; padding: 10px 20px; }
    </style>
""", unsafe_allow_html=True)

# 2. 데이터 수집 (나스닥 공식 TXT)
@st.cache_data(ttl=3600)
def fetch_nasdaq_data(date_str):
    url = f"https://www.nasdaqtrader.com/dynamic/symdir/regsho/nasdaqth{date_str}.txt"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200 and "Symbol" in resp.text:
            df = pd.read_csv(url, sep='|')[:-1]
            df.columns = df.columns.str.strip()
            return set(df['Symbol'].unique()), df[['Symbol', 'Security Name']]
    except: pass
    return None, None

# 3. 시총 데이터 가져오기 (yfinance 활용)
def get_market_cap(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info
        cap = info.get('market_cap', 0)
        if cap >= 1e9: return f"{cap/1e9:.1f}B"
        elif cap >= 1e6: return f"{cap/1e6:.1f}M"
        return "N/A"
    except: return "N/A"

# 4. 30거래일 정밀 분석 (오류 보정 최적화)
@st.cache_data(ttl=3600)
def run_pro_analysis():
    latest_df = None
    latest_date = None
    # 최신 데이터 확보
    for i in range(7):
        d = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
        syms, raw = fetch_nasdaq_data(d)
        if syms:
            latest_date, latest_df = d, raw
            break
    
    if latest_df is None: return None, None

    symbols = latest_df['Symbol'].tolist()
    days_map = {sym: 1 for sym in symbols}
    missing_count = {sym: 0 for sym in symbols}
    active = {sym: True for sym in symbols}
    
    # 30거래일만 '증거 기반'으로 추적 (60일 오류 방지)
    curr_dt = datetime.strptime(latest_date, '%Y%m%d')
    checked_days, offset = 1, 1
    while checked_days < 30 and offset < 50:
        c_date = (curr_dt - timedelta(days=offset)).strftime('%Y%m%d')
        prev_syms, _ = fetch_nasdaq_data(c_date)
        offset += 1
        if prev_syms is not None:
            checked_days += 1
            for sym in symbols:
                if active[sym]:
                    if sym in prev_syms:
                        days_map[sym] += 1
                        missing_count[sym] = 0
                    else:
                        missing_count[sym] += 1
                        # 2일 연속 부재 시에만 종료 (더 엄격하게)
                        if missing_count[sym] >= 2: active[sym] = False

    latest_df['Days'] = latest_df['Symbol'].map(days_map)
    return latest_df, latest_date

# 5. UI 메인 대시보드
st.title("🛡️ RegSHO 공매도 감시 Pro")
df, update_date = run_pro_analysis()

if df is not None:
    # 상단 요약 카드 (Summary Cards)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("등록 티커", len(df))
    m2.metric("위험(13일+)", len(df[df['Days'] >= 13]))
    m3.metric("주의(5일+)", len(df[(df['Days'] >= 5) & (df['Days'] < 13)]))
    m4.metric("신규 진입", "분석 중...") # 신규 로직 추가 가능

    st.divider()

    # 메뉴 탭 구성
    tab_all, tab_high, tab_caution = st.tabs(["전체 목록", "고위험 (13일+)", "주의 (5일+)"])

    # 검색 및 필터
    search = st.text_input("🔍 티커 입력", "").upper()

    def show_table(target_df):
        if search: target_df = target_df[target_df['Symbol'].str.contains(search)]
        # 시총 데이터 병렬 로드 (속도 향상)
        if not target_df.empty and st.button(f"현재 목록 시총 데이터 불러오기 ({len(target_df)}건)"):
            with st.spinner("시총 분석 중..."):
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    target_df['시총'] = list(executor.map(get_market_cap, target_df['Symbol']))
        
        st.dataframe(target_df.sort_values('Days', ascending=False), 
                     use_container_width=True, hide_index=True,
                     column_config={"Days": st.column_config.NumberColumn("연속 등재일", format="%d일 🔥")})

    with tab_all: show_table(df)
    with tab_high: show_table(df[df['Days'] >= 13])
    with tab_caution: show_table(df[(df['Days'] >= 5) & (df['Days'] < 13)])

else:
    st.error("나스닥 서버 연결 실패")
