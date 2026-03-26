import streamlit as st
from supabase import create_client
import requests

# 1. 수파베이스 설정
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. 텔레그램 설정
TOKEN = "8306599736:AAHwT_jhT9DHJqdWubOQoL1JuNlBbMjswGw"
CHAT_ID = "8182795005"

def send_test_telegram():
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": "🔔 <b>[NSD PRO]</b> 스트림릿 텔레그램 테스트 성공!", "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=5)
        st.success("✅ 텔레그램 테스트 메시지 발송 완료!")
    except Exception as e:
        st.error(f"❌ 발송 실패: {e}")

st.title("🚀 NSD PRO 컨트롤 패널")

# 텔레그램 테스트 버튼
st.subheader("🧪 시스템 테스트")
if st.button("🔔 텔레그램 연동 테스트"):
    send_test_telegram()

st.divider()

# 감시 종목 설정
st.subheader("⚙️ 감시 리스트 설정")
st.write("감시할 티커 (쉼표로 구분. 예: BNAI, EMPD)")

current_tickers = ""
try:
    res = supabase.table('user_config').select('watchlist').eq('id', 1).execute()
    if res.data and len(res.data) > 0:
        current_tickers = res.data[0].get('watchlist', '')
except Exception as e:
    pass 

new_tickers = st.text_input("종목 입력", value=current_tickers, label_visibility="collapsed")

if st.button("💾 설정 저장"):
    try:
        supabase.table('user_config').upsert({"id": 1, "watchlist": new_tickers}).execute()
        st.success("✅ 저장 완료! 파이썬 서버가 즉시 새 종목으로 감시를 시작합니다.")
        current_tickers = new_tickers 
    except Exception as e:
        st.error(f"❌ 저장 실패: {e}")

st.info(f"📋 **현재 감시 중인 종목:** {current_tickers if current_tickers else '없음'}")
