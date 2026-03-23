import streamlit as st
from supabase import create_client

SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("🚨 NSD PRO 공시 감시 센터")

# 감시 종목 설정
res = supabase.table("user_config").select("watchlist").eq("id", 1).execute()
current = res.data[0]['watchlist'] if res.data else ""

new_watchlist = st.text_input("감시 종목 (쉼표로 구분)", value=current)
if st.button("설정 저장"):
    supabase.table("user_config").update({"watchlist": new_watchlist.upper()}).eq("id", 1).execute()
    st.success("이제 일꾼이 새 종목을 감시합니다!")

st.divider()
st.subheader("📋 현재 감시 중인 종목")
st.code(new_watchlist.upper())
st.info("알림은 텔레그램으로 전송됩니다. 등재일 기능은 제거되었습니다.")
