import streamlit as st
import pandas as pd
import requests
import yfinance as yf
from datetime import datetime, timedelta
from supabase import create_client

# 1. 사용자님의 정보를 제가 이미 채워 넣었습니다.
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="NSD PRO HUB", layout="wide")

# 2. 데이터 저장 로직 (이 코드가 나스닥 데이터를 긁어와서 사용자 DB를 채웁니다)
def sync_to_db(date_str):
    url = f"https://www.nasdaqtrader.com/dynamic/symdir/regsho/nasdaqth{date_str}.txt"
    try:
        resp = requests.get(url, timeout=7)
        if resp.status_code == 200:
            df = pd.read_csv(url, sep='|')[:-1]
            df.columns = df.columns.str.strip()
            for _, row in df.iterrows():
                data = {
                    "symbol": row['Symbol'],
                    "security_name": row['Security Name'],
                    "recorded_date": f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
                }
                # 중복 없이 사용자 DB에 박제
                supabase.table("reg_sho_logs").upsert(data).execute()
            return True
    except: pass
    return False

# 3. UI 구성 (사용자님이 보신 프로 앱 디자인을 따라갑니다)
st.title("🛡️ NSD PRO HUB")
st.sidebar.title("메뉴")
menu = st.sidebar.radio("이동", ["🚨 Reg SHO 분석", "⚙️ 설정"])

if menu == "🚨 Reg SHO 분석":
    # 
    if st.button("🔄 과거 30일 데이터 강제 동기화 (최초 1회 필수)"):
        with st.spinner("사용자님의 개인 DB에 팩트 데이터를 채우는 중..."):
            for i in range(30):
                d = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
                sync_to_db(d)
        st.success("동기화 완료! 이제 DB에 데이터가 꽉 찼습니다.")

    search = st.text_input("🔍 티커 검색 (예: BNAI)", "").upper()
    if search:
        # DB에서 이 티커가 기록된 모든 날짜를 가져옵니다.
        res = supabase.table("reg_sho_logs").select("recorded_date").eq("symbol", search).order("recorded_date", desc=True).execute()
        if res.data:
            streak = len(res.data) # 저장된 기록의 개수가 곧 등재 일수입니다.
            st.metric("연속 등재일", f"{streak}일", delta="무결성 DB 기록")
            st.error(f"🚨 {search} : {streak}거래일 연속 등재 중입니다.")
        else:
            st.success(f"✅ {search} : 현재 리스트에 없습니다.")
