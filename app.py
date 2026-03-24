import streamlit as st
import requests
from supabase import create_client

# 1. 고정 설정 (수정 불필요)
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
TELEGRAM_TOKEN = "8306599736:AAHwT_jhT9DHJqdWubOQoL1JuNlBbMjswGw"
CHAT_ID = "8182795005"

st.set_page_config(page_title="NSD PRO 공시 감시 센터", page_icon="🚨")

# 연결 함수
@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    supabase = init_connection()
    
    st.title("🚨 NSD PRO 공시 감시 센터")
    st.success("✅ 시스템 정상 작동 중 (공시 감시 전용)")

    # --- [섹션 1: 텔레그램 연결 테스트] ---
    st.divider()
    st.subheader("🧪 시스템 테스트")
    if st.button("🔔 텔레그램으로 테스트 메시지 보내기"):
        test_msg = "✅ NSD PRO 스트림릿 테스트 메시지입니다. 연결이 아주 좋습니다!"
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        res = requests.post(url, data={"chat_id": CHAT_ID, "text": test_msg})
        if res.status_code == 200:
            st.toast("테스트 메시지를 보냈습니다! 텔레그램을 확인하세요.")
        else:
            st.error("테스트 실패. 토큰이나 챗ID를 확인해주세요.")

    # --- [섹션 2: 감시 리스트 관리] ---
    st.divider()
    st.subheader("⚙️ 감시 리스트 설정")
    res = supabase.table("user_config").select("watchlist").eq("id", 1).execute()
    
    if res.data:
        current_watchlist = res.data[0]['watchlist']
        new_watchlist = st.text_input("감시할 티커 (쉼표로 구분)", value=current_watchlist)
        
        if st.button("💾 설정 저장"):
            supabase.table("user_config").update({"watchlist": new_watchlist.upper()}).eq("id", 1).execute()
            st.success("새로운 리스트가 저장되었습니다. 일꾼이 곧 반영합니다.")
            st.rerun()
            
        st.info(f"📋 **현재 감시 중:** {new_watchlist.upper()}")
    else:
        st.warning("데이터베이스에서 설정값을 읽어올 수 없습니다.")

except Exception as e:
    st.error(f"⚠️ 연결 오류 발생: {e}")
    st.write("Supabase 프로젝트가 'Active' 상태인지 확인하세요.")

st.divider()
st.caption("참고: 등재일 데이터는 제거되었습니다. 이제 오직 공시에만 집중합니다.")
