import streamlit as st
from supabase import create_client

# 1. 고정 설정
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="NSD PRO 실시간 공시", layout="wide")

st.title("🚨 NSD PRO 실시간 공시 감시")

# 2. 감시 종목 설정 섹션
with st.sidebar:
    st.header("⚙️ 감시 설정")
    res = supabase.table("user_config").select("watchlist").eq("id", 1).execute()
    current_watchlist = res.data[0]['watchlist'] if res.data else ""
    
    new_watchlist = st.text_input("감시 티커 입력 (쉼표 구분)", value=current_watchlist)
    
    if st.button("설정 저장"):
        supabase.table("user_config").update({"watchlist": new_watchlist.upper()}).eq("id", 1).execute()
        st.success("저장 완료! 이제 일꾼이 새 종목을 감시합니다.")

# 3. 메인 화면
st.info("현재 파이썬애니웨어 일꾼이 SEC 공시를 실시간 감시 중입니다. 공시는 텔레그램으로 즉시 전송됩니다.")

st.subheader("📋 현재 감시 중인 종목")
st.code(new_watchlist.upper())

st.write("---")
st.caption("참고: 등재일 데이터는 신뢰성 문제로 인해 제거되었습니다. 이제 오직 공시에만 집중합니다.")
