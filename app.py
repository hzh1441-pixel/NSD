import streamlit as st
from supabase import create_client

# 1. 고정 설정 (이 정보가 정확해야 에러가 안 납니다)
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"

st.set_page_config(page_title="NSD PRO 공시 감시 센터", page_icon="🚨")

# 연결 함수 (에러 방지용 캐싱)
@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    supabase = init_connection()
    
    st.title("🚨 NSD PRO 공시 감시 센터")
    st.success("✅ 시스템 정상 작동 중 (공시 감시 전용)")

    # 감시 종목 설정
    st.subheader("⚙️ 감시 리스트 관리")
    res = supabase.table("user_config").select("watchlist").eq("id", 1).execute()
    
    if res.data:
        current_watchlist = res.data[0]['watchlist']
        new_watchlist = st.text_input("감시할 티커 (쉼표 구분)", value=current_watchlist)
        
        if st.button("설정 저장"):
            supabase.table("user_config").update({"watchlist": new_watchlist.upper()}).eq("id", 1).execute()
            st.toast("설정이 저장되었습니다!")
            st.rerun()
            
        st.divider()
        st.subheader("📋 현재 실시간 감시 중")
        st.code(new_watchlist.upper())
        st.info("알림은 텔레그램으로 24시간 전송됩니다.")
    else:
        st.warning("데이터베이스에서 설정값을 읽어올 수 없습니다. 테이블 정보를 확인해주세요.")

except Exception as e:
    st.error(f"⚠️ 연결 오류 발생: {e}")
    st.write("1. Supabase 프로젝트가 'Paused' 상태인지 확인하세요.")
    st.write("2. URL과 API Key가 정확한지 확인하세요.")
