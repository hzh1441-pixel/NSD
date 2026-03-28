import streamlit as st
from supabase import create_client
import requests
import pandas as pd

# --- [1. 기본 설정 및 보안 연결] ---
st.set_page_config(page_title="NSD PRO Dashboard", layout="wide") 

SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

TOKEN = "8306599736:AAHwT_jhT9DHJqdWubOQoL1JuNlBbMjswGw"
CHAT_ID = "8182795005"

# --- [2. 핵심 기능 함수 (기존 로직 동일)] ---
def send_test_telegram():
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": "🔔 <b>[NSD PRO]</b> 시스템 연동 테스트 성공!", "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=5)
        st.success("✅ 텔레그램 메시지가 발송되었습니다.")
    except Exception as e:
        st.error(f"❌ 발송 실패: {e}")

def load_settings():
    try:
        res = supabase.table('user_config').select('watchlist').eq('id', 1).execute()
        return res.data[0].get('watchlist', '') if res.data else ""
    except: return ""

# --- [3. UI 레이아웃 설계] ---
st.title("💹 NSD PRO : 실시간 나스닥 터미널")

# 상단 종목 카드 (현재 감시 중인 종목 시각화)
watchlist_str = load_settings()
tickers = [t.strip().upper() for t in watchlist_str.split(',') if t.strip()]

if tickers:
    cols = st.columns(len(tickers))
    for i, ticker in enumerate(tickers):
        with cols[i]:
            st.metric(label="Monitoring", value=ticker, delta="SEC 24H")
else:
    st.info("현재 감시 중인 종목이 없습니다. [설정] 탭에서 종목을 추가하세요.")

st.divider()

# 메인 기능 탭 분할 (보기 좋게 정리)
tab1, tab2, tab3 = st.tabs(["📋 감시 리스트 설정", "🧪 시스템 테스트", "📊 데이터 분석(예정)"])

with tab1:
    st.subheader("⚙️ 종목 업데이트")
    st.write("감시할 티커를 입력하세요 (쉼표로 구분)")
    # 입력창
    new_tickers = st.text_input("Ticker Input", value=watchlist_str, label_visibility="collapsed")
    
    if st.button("💾 설정 저장 및 엔진 동기화"):
        try:
            # 기존과 동일한 저장 로직 (id=1 고정)
            supabase.table('user_config').upsert({"id": 1, "watchlist": new_tickers}).execute()
            st.success("✅ 성공적으로 저장되었습니다! 파이썬 엔진이 즉시 새 목록을 감시합니다.")
            st.rerun() # 화면 새로고침해서 상단 카드 업데이트
        except Exception as e:
            st.error(f"❌ 저장 실패: {e}")

with tab2:
    st.subheader("📡 연결 상태 확인")
    st.write("텔레그램 알림이 정상적으로 오는지 확인합니다.")
    if st.button("🔔 텔레그램 테스트 알림 보내기"):
        send_test_telegram()

with tab3:
    st.write("📈 **Reg Sho 및 FTD 분석 데이터**")
    st.info("이곳에 나중에 Reg Sho 일수와 차트가 들어올 예정입니다.")

# 하단 상태바
st.divider()
st.caption(f"시스템 상태: 정상 가동 중 | 마지막 동기화: {pd.Timestamp.now().strftime('%H:%M:%S')}")
