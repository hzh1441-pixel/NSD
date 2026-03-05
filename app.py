import streamlit as st
from supabase import create_client

SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.write("🔍 DB 연결 팩트 체크 시작")

try:
    res = supabase.table("user_config").select("*").execute()
    st.success(f"✅ DB 연결 성공! 현재 테이블 데이터: {res.data}")
except Exception as e:
    st.error(f"❌ DB 연결 실패 또는 테이블 없음: {e}")
