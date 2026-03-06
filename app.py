import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client
import requests

# ==========================================
# 1. 팩트 데이터 및 인프라 (절대 수정 금지)
# ==========================================
PHOTO_FACTS = {
    "AREB": 27, "VEEE": 25, "ELPW": 21, "SVRN": 20, "CISS": 19, "RVSN": 16,
    "HOOX": 15, "PBOG": 14, "SMX": 13, "UOKA": 13, "BNAI": 12, "MYCH": 12,
    "GFAI": 11, "BRTX": 10, "NCI": 10, "HUBC": 10, "DTST": 10, "HBR": 9,
    "NVDL": 9, "RIME": 9, "SOND": 9, "LFS": 8, "LGHL": 8, "PDC": 8, "KODK": 8,
    "XTKG": 7, "CDIO": 6, "GGLS": 5, "GV": 5, "MGRX": 5, "PFSA": 5, "RUBI": 5,
    "BHAT": 4, "DUOG": 3, "FFAI": 3, "AMZD": 2, "APPX": 2, "IONZ": 2
}

SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
TELEGRAM_TOKEN = "8306599736:AAHwT_jhT9DHJqdWubOQoL1JuNlBbMjswGw"
CHAT_ID = "8182795005"

st.set_page_config(page_title="NSD PRO", layout="wide")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================
# 2. 영구 보존 엔진 (앱 구동 시 최초 1회만 실행)
# ==========================================
if "app_initialized" not in st.session_state:
    try:
        res = supabase.table("user_config").select("*").eq("id", 1).execute()
        if res.data:
            st.session_state.watch_list = res.data[0].get("watchlist", "")
            st.session_state.alert_on = res.data[0].get("alert_enabled", True)
        else:
            st.session_state.watch_list = ""
            st.session_state.alert_on = True
    except Exception:
        st.session_state.watch_list = ""
        st.session_state.alert_on = True
    
    st.session_state.app_initialized = True

# ==========================================
# 3. UI 및 동기화
# ==========================================
st.title("승현쓰껄~ㅋ")

with st.expander("🔔 실시간 알림 및 감시 종목 설정 (영구 저장)", expanded=True):
    current_alert = st.toggle("텔레그램 알림 활성화", value=st.session_state.alert_on)
    current_watch = st.text_input("감시 티커 입력 (쉼표 구분 후 엔터)", value=st.session_state.watch_list).upper()

    if current_alert != st.session_state.alert_on or current_watch != st.session_state.watch_list:
        try:
            supabase.table("user_config").upsert({
                "id": 1,
                "watchlist": current_watch,
                "alert_enabled": current_alert
            }).execute()
            
            st.session_state.watch_list = current_watch
            st.session_state.alert_on = current_alert
            st.toast("✅ 서버에 영구 저장되었습니다.")
        except Exception as e:
            st.error(f"❌ DB 저장 실패: {e}")

    col1, col2 = st.columns([4, 1])
    with col1:
        if st.session_state.watch_list:
            st.success(f"🛰️ 현재 서버 감시 중: {st.session_state.watch_list}")
    with col2:
        if st.button("🚀 테스트 발송"):
            try:
                msg = f"✅ NSD PRO: 연동 정상\n감시 목록: {st.session_state.watch_list}"
                requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                              data={"chat_id": CHAT_ID, "text": msg}, timeout=5)
                st.toast("테스트 발송 성공!")
            except Exception:
                st.error("발송 실패")

# ==========================================
# 🔥 4. 무적의 데이터 엔진 (SEC 공식 종목명 100% 실시간 연동)
# ==========================================
@st.cache_data(ttl=86400) # 하루에 한 번만 SEC 공식 명단표를 가져옵니다 (속도 저하 방지)
def get_sec_company_names():
    try:
        headers = {'User-Agent': 'NSD_PRO_App/1.0'}
        # SEC 공식 서버에서 실시간 티커-종목명 매칭표 다운로드
        res = requests.get("https://www.sec.gov/files/company_tickers.json", headers=headers, timeout=5)
        if res.status_code == 200:
            return {item['ticker']: item['title'] for item in res.json().values()}
    except:
        pass
    return {}

def fetch_verified_data():
    try:
        # 1. SEC 공식 이름표 획득
        sec_names = get_sec_company_names()
        
        # 2. DB에서 3월 4일 이후의 새 도장들 가져오기
        res = supabase.table("reg_sho_logs").select("symbol, recorded_date").gt("recorded_date", "2026-03-04").execute()
        df = pd.DataFrame(res.data) if res.data else pd.DataFrame()
        
        rows = []
        processed_symbols = set()
        
        # [VIP 명단 처리]
        for sym, base_days in PHOTO_FACTS.items():
            added_days = 0
            if not df.empty and 'symbol' in df.columns:
                sym_data = df[df['symbol'] == sym]
                if not sym_data.empty:
                    added_days = len(sym_data['recorded_date'].unique())
            
            # 🚨 핵심 팩트: DB 찌꺼기 무시하고 SEC 공식 이름표에서 진짜 이름을 찾아옴!
            real_name = sec_names.get(sym, sym) 
            
            rows.append({
                "등재일": base_days + added_days,
                "로고": f"https://www.google.com/s2/favicons?sz=128&domain={sym}.com",
                "티커": sym,
                "종목명": real_name
            })
            processed_symbols.add(sym)
            
        # [사냥개가 물어온 신규 종목 처리 (예: WHLR)]
        if not df.empty and 'symbol' in df.columns:
            new_symbols = df[~df['symbol'].isin(processed_symbols)]['symbol'].unique()
            for sym in new_symbols:
                sym_data = df[df['symbol'] == sym]
                added_days = len(sym_data['recorded_date'].unique())
                
                # 신규 종목도 당연히 SEC 공식 이름으로 맵핑
                real_name = sec_names.get(sym, sym)
                
                rows.append({
                    "등재일": added_days,
                    "로고": f"https://www.google.com/s2/favicons?sz=128&domain={sym}.com",
                    "티커": sym,
                    "종목명": real_name
                })
                
        return pd.DataFrame(rows)
    except Exception as e:
        st.error(f"데이터 엔진 오류: {e}")
        return pd.DataFrame()




# ==========================================
# 5. 메인 리스트 렌더링
# ==========================================
active_df = fetch_verified_data()
search = st.text_input("🔍 목록 내 검색", "").upper()

if not active_df.empty:
    if search:
        active_df = active_df[active_df['티커'].str.contains(search)]
    
    st.dataframe(
        active_df.sort_values(by="등재일", ascending=False),
        column_order=["등재일", "로고", "티커", "종목명"],
        column_config={
            "등재일": st.column_config.NumberColumn("등재일", format="%d 일", width="small"),
            "로고": st.column_config.ImageColumn("", width="small"),
            "티커": st.column_config.TextColumn("티커"),
            "종목명": st.column_config.TextColumn("종목명")
        }, 
        use_container_width=True, 
        hide_index=True
    )
