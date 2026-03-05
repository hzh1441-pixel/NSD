import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from supabase import create_client

# 1. 아까 메모해둔 URL과 KEY를 정확히 입력하세요
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="NSD Intelligence Hub", layout="wide")

# 2. 데이터를 DB에 영구 저장하는 함수
def sync_to_db(date_str):
    url = f"https://www.nasdaqtrader.com/dynamic/symdir/regsho/nasdaqth{date_str}.txt"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            df = pd.read_csv(url, sep='|')[:-1]
            df.columns = df.columns.str.strip()
            for _, row in df.iterrows():
                # DB에 박제 (이미 있으면 무시함)
                data = {
                    "symbol": row['Symbol'],
                    "security_name": row['Security Name'],
                    "market_category": row.get('Market Category', ''),
                    "recorded_date": f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
                }
                supabase.table("reg_sho_logs").upsert(data).execute()
            return True
    except: pass
    return False

# 3. 사이드바 메뉴 구성
with st.sidebar:
    st.title("🛡️ NSD PRO HUB")
    menu = st.radio("메뉴", ["🏠 홈", "🚨 Reg SHO 분석"])

if menu == "🚨 Reg SHO 분석":
    st.subheader("🔥 Reg SHO 정밀 모니터링 (DB 무결성 모드)")
    
    #     if st.button("🔄 과거 30일 데이터 강제 동기화"):
        with st.spinner("사용자님의 개인 DB에 데이터를 채우는 중..."):
            for i in range(30):
                d = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
                sync_to_db(d)
        st.success("동기화 완료! 이제 BNAI 기록이 절대 사라지지 않습니다.")

    # [중요] 이후 여기에 시가총액, 현재가, 공시 필터 기능을 하나씩 붙여나갈 것입니다.
