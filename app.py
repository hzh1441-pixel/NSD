import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client
import requests

# 1. [성역] 사진 실증 마스터 데이터 (수정 절대 금지)
PHOTO_FACTS = {
    "AREB": 27, "VEEE": 25, "ELPW": 21, "SVRN": 20, "CISS": 19, "RVSN": 16,
    "HOOX": 15, "PBOG": 14, "SMX": 13, "UOKA": 13, "BNAI": 12, "MYCH": 12,
    "GFAI": 11, "BRTX": 10, "NCI": 10, "HUBC": 10, "DTST": 10, "HBR": 9,
    "NVDL": 9, "RIME": 9, "SOND": 9, "LFS": 8, "LGHL": 8, "PDC": 8, "KODK": 8,
    "XTKG": 7, "CDIO": 6, "GGLS": 5, "GV": 5, "MGRX": 5, "PFSA": 5, "RUBI": 5,
    "BHAT": 4, "DUOG": 3, "FFAI": 3, "AMZD": 2, "APPX": 2, "IONZ": 2
}

# 2. 시스템 인프라 설정
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

TELEGRAM_TOKEN = "8306599736:AAHwT_jhT9DHJqdWubOQoL1JuNlBbMjswGw"
CHAT_ID = "8182795005"

st.set_page_config(page_title="NSD PRO", layout="wide")

# --- 영구 보존 엔진: DB에서 설정 불러오기 ---
def get_config_from_db():
    try:
        res = supabase.table("user_config").select("watchlist, alert_enabled").eq("id", 1).execute()
        if res.data:
            return res.data[0]
    except Exception:
        pass
    return {"watchlist": "", "alert_enabled": True}

# 앱 시작 시 초기화 (재부팅 시 데이터 복구의 핵심)
if 'initialized' not in st.session_state:
    db_cfg = get_config_from_db()
    st.session_state['watchlist'] = db_cfg['watchlist']
    st.session_state['alert_enabled'] = db_cfg['alert_enabled']
    st.session_state['initialized'] = True

# 저장 함수: 입력 즉시 DB에 동기화
def sync_db_config():
    try:
        # 입력창(key="w_input")과 토글(key="a_toggle")의 최신 값을 DB에 저장
        w_val = st.session_state.w_input.upper()
        a_val = st.session_state.a_toggle
        supabase.table("user_config").upsert({
            "id": 1,
            "watchlist": w_val,
            "alert_enabled": a_val
        }).execute()
        # 세션 상태도 최신화
        st.session_state['watchlist'] = w_val
        st.session_state['alert_enabled'] = a_val
        st.toast("✅ 설정이 서버에 영구 저장되었습니다.")
    except Exception:
        st.error("❌ 저장 실패: DB 연결 상태를 확인하세요.")

st.title("🛡️ Reg sho 등재 목록")

# --- UI 상단: 24시간 실시간 감시 설정 ---
with st.expander("🔔 실시간 알림 및 감시 종목 설정 (영구 저장)", expanded=True):
    # 토글 (on_change를 사용하여 즉시 저장)
    st.toggle(
        "텔레그램 알림 활성화",
        value=st.session_state['alert_enabled'],
        key="a_toggle",
        on_change=sync_db_config
    )
    
    # 입력창 (on_change를 사용하여 엔터키 입력 시 즉시 저장)
    st.text_input(
        "감시 티커 입력 (쉼표 구분)",
        value=st.session_state['watchlist'],
        key="w_input",
        on_change=sync_db_config,
        placeholder="예: BNAI, TSLA"
    )

    col1, col2 = st.columns([4, 1])
    with col1:
        if st.session_state['watchlist']:
            st.success(f"🛰️ 현재 서버 감시 중: {st.session_state['watchlist']}")
    with col2:
        if st.button("🚀 테스트 발송"):
            try:
                msg = f"✅ NSD PRO: 연동 정상\n감시 목록: {st.session_state['watchlist']}"
                requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                              data={"chat_id": CHAT_ID, "text": msg}, timeout=5)
                st.toast("테스트 알림 전송 완료")
            except Exception:
                st.error("알림 전송 실패")

# 3. 데이터 엔진 (순서 100% 보존: 등재일 > 로고 > 티커 > 종목명)
def get_verified_data():
    try:
        res = supabase.table("reg_sho_logs").select("symbol, security_name, recorded_date").execute()
        if not res.data: return None
        df = pd.DataFrame(res.data)
        df['recorded_date'] = pd.to_datetime(df['recorded_date']).dt.date
        latest_date = df['recorded_date'].max()
        
        # 3/4 이후 실제 데이터 기반 추가 날짜 산출
        extra_days = len(df[df['recorded_date'] > datetime(2026, 3, 4).date()]['recorded_date'].unique())
        
        current_market = df[df['recorded_date'] == latest_date]
        final_rows = []
        for _, row in current_market.iterrows():
            sym, name = row['symbol'], row['security_name'].upper()
            if any(kw in name for kw in ["ETF", "TRUST", "FUND", "FD"]): continue
