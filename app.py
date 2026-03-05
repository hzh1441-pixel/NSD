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

# 2. 인프라 설정
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

TELEGRAM_TOKEN = "8306599736:AAHwT_jhT9DHJqdWubOQoL1JuNlBbMjswGw"
CHAT_ID = "8182795005"

st.set_page_config(page_title="NSD PRO", layout="wide")

# --- [영구 저장 로직] 앱을 꺼도 사라지지 않는 핵심 장치 ---
def get_user_config():
    """앱 시작 시 DB에서 사용자 설정을 무조건 불러옴"""
    try:
        res = supabase.table("user_config").select("*").eq("id", 1).execute()
        return res.data[0] if res.data else {"watchlist": "", "alert_enabled": True}
    except Exception:
        return {"watchlist": "", "alert_enabled": True}

def save_user_config(watchlist, alert_enabled):
    """변경 즉시 DB에 저장하여 영구 박제"""
    try:
        supabase.table("user_config").upsert({
            "id": 1, 
            "watchlist": watchlist, 
            "alert_enabled": alert_enabled
        }).execute()
    except Exception:
        pass

# 앱 구동 즉시 DB 데이터 로드 (폰 재부팅 대응)
if 'init' not in st.session_state:
    config = get_user_config()
    st.session_state.user_watchlist = config['watchlist']
    st.session_state.alert_on = config['alert_enabled']
    st.session_state.init = True

# --- UI 상단: 24시간 감시 센터 ---
st.title("승현쓰껄ㅋ")

with st.expander("🔔 실시간 알림 및 감시 종목 설정", expanded=True):
    alert_on = st.toggle("텔레그램 알림 활성화", value=st.session_state.alert_on)
    
    watch_input = st.text_input(
        "감시 티커 입력 (쉼표 구분)", 
        value=st.session_state.user_watchlist,
        placeholder="예: BNAI, TSLA"
    ).upper()
    
    # 변경 사항 감지 시 즉시 저장
    if (watch_input != st.session_state.user_watchlist) or (alert_on != st.session_state.alert_on):
        st.session_state.user_watchlist = watch_input
        st.session_state.alert_on = alert_on
        save_user_config(watch_input, alert_on)

    col1, col2 = st.columns([4, 1])
    with col1:
        if watch_input:
            st.success(f"🛰️ 24시간 감시 중: {watch_input}")
    with col2:
        # [복구] 테스트 알림 버튼 (오타 수리 완료)
        if st.button("🚀 테스트 발송"):
            msg = f"✅ NSD PRO: 연결 상태 정상\n현재 감시 중: {watch_input}"
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                          data={"chat_id": CHAT_ID, "text": msg})
            st.toast("테스트 발송 완료")

# 3. 데이터 엔진 (순서 100% 보존: 등재일 > 로고 > 티커 > 종목명)
def get_verified_data():
    try:
        res = supabase.table("reg_sho_logs").select("symbol, security_name, recorded_date").execute()
        if not res.data: return None
        df = pd.DataFrame(res.data)
        df['recorded_date'] = pd.to_datetime(df['recorded_date']).dt.date
        latest_date = df['recorded_date'].max()
        
        extra_days = len(df[df['recorded_date'] > datetime(2026, 3, 4).date()]['recorded_date'].unique())
        
        current_market = df[df['recorded_date'] == latest_date]
        final_rows = []
        for _, row in current_market.iterrows():
            sym, name = row['symbol'], row['security_name'].upper()
            if any(kw in name for kw in ["ETF", "TRUST", "FUND", "FD", "TARGET", "DAILY"]): continue
            
            days = (PHOTO_FACTS[sym] + extra_days) if sym in PHOTO_FACTS else len(df[df['symbol'] == sym])
            
            # 🔥 [UI 순서 고정] 등재일 > 로고 > 티커 > 종목명
            final_rows.append({
                "등재일": days,
                "로고": f"https://www.google.com/s2/favicons?sz=128&domain={sym}.com",
                "티커": sym,
                "종목명": name
            })
        return pd.DataFrame(final_rows)
    except Exception:
        return None

active_df = get_verified_data()
if active_df is not None:
    st.dataframe(active_df.sort_values(by="등재일", ascending=False),
        column_config={
            "등재일": st.column_config.NumberColumn("등재일", format="%d 일", width="small"),
            "로고": st.column_config.ImageColumn("", width="small"),
            "티커": st.column_config.TextColumn("티커"),
            "종목명": st.column_config.TextColumn("종목명")
        }, use_container_width=True, hide_index=True)
