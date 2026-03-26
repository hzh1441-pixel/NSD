import streamlit as st
from supabase import create_client
import requests

# --- [Supabase 설정] ---
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- [Telegram 설정 (테스트용)] ---
TOKEN = "8306599736:AAHwT_jhT9DHJqdWubOQoL1JuNlBbMjswGw"
CHAT_ID = "8182795005"

def send_test_telegram():
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": "🔔 <b>[NSD PRO]</b> 시스템 연동 테스트 완료!", "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload)
        st.success("테스트 메시지 발송 완료!")
    except Exception as e:
        st.error(f"발송 실패: {e}")

# --- [UI 구성] ---
st.title("🚀 NSD PRO 컨트롤 패널")

st.subheader("🧪 시스템 테스트")
if st.button("🔔 텔레그램으로 테스트 메시지 보내기"):
    send_test_telegram()

st.divider()

st.subheader("⚙️ 감시 리스트 설정")
st.write("감시할 티커 (쉼표로 구분)")

# 1. Supabase에서 현재 설정 불러오기
current_tickers = ""
try:
    res = supabase.table('user_config').select('watchlist').eq('id', 1).execute()
    if res.data and 'watchlist' in res.data[0]:
        current_tickers = res.data[0]['watchlist']
except Exception as e:
    st.error("데이터베이스 연결 오류. 관리자에게 문의하세요.")

# 2. 사용자 입력 받기
new_tickers = st.text_input("종목 입력", value=current_tickers, label_visibility="collapsed")

# 3. 저장 버튼 처리
if st.button("💾 설정 저장"):
    try:
        # id가 1인 데이터(또는 없으면 새로) 업데이트
        supabase.table('user_config').upsert({"id": 1, "watchlist": new_tickers}).execute()
        st.success("설정이 성공적으로 저장되었습니다!")
        # 새로고침 효과를 위해 다시 불러오기
        current_tickers = new_tickers 
    except Exception as e:
        st.error(f"저장 실패: {e}")

st.info(f"📋 **현재 감시 중:** {current_tickers if current_tickers else '없음'}")
