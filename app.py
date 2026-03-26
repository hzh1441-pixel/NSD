import streamlit as st
from supabase import create_client

# 1. 수파베이스 연결
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("🚀승현쓰껄")
st.subheader("⚙️ 감시 리스트 설정")
st.write("감시할 티커 (쉼표로 구분하여 입력. 예: BNAI, EMPD)")

# 2. 현재 DB 데이터 불러오기
current_tickers = ""
try:
    res = supabase.table('user_config').select('watchlist').eq('id', 1).execute()
    if res.data and len(res.data) > 0:
        current_tickers = res.data[0].get('watchlist', '')
except Exception as e:
    st.error(f"DB 연결 에러 (수파베이스 테이블 설정을 확인하세요): {e}")

# 3. 입력창 생성
new_tickers = st.text_input("종목 입력", value=current_tickers, label_visibility="collapsed")

# 4. DB에 저장하기 (Upsert: 없으면 만들고 있으면 덮어씀)
if st.button("💾 설정 저장"):
    try:
        supabase.table('user_config').upsert({"id": 1, "watchlist": new_tickers}).execute()
        st.success("✅ 스트림릿에서 성공적으로 저장되었습니다! 파이썬 서버가 즉시 감시를 갱신합니다.")
        current_tickers = new_tickers 
    except Exception as e:
        st.error(f"저장 실패: {e}")

st.info(f"📋 **현재 데이터베이스에 저장된 종목:** {current_tickers if current_tickers else '없음'}")
