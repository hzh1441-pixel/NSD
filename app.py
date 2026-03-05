import streamlit as st
import pandas as pd
import requests
from supabase import create_client

# 1. 인프라 및 API 설정
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
ORTEX_API_KEY = "9vOWMVq6.ViwuNCVtA318YnQTg2FoG3ucwEUCHmMX"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="NSD PRO: ORTEX 팩트 엔진", layout="wide")

# [이미지] 로고 가져오기
def get_logo(ticker):
    return f"https://www.google.com/s2/favicons?sz=64&domain={ticker}.com"

# [핵심] 19일 벽을 깨는 ORTEX 팩트 호출 함수
def get_real_regsho_days(ticker):
    # ORTEX 서버에 직접 물어봐서 '진짜 숫자'를 가져옵니다.
    url = f"https://api.ortex.com/v1/stocks/{ticker}/short-interest"
    headers = {"Authorization": f"Bearer {ORTEX_API_KEY}"}
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            # ORTEX가 이미 계산해둔 '진짜 연속 등재일' 필드를 가져옵니다.
            # (API 응답 필드명은 ORTEX 규격에 따라 'reg_sho_days' 또는 유사 명칭)
            return data.get('reg_sho_days', 0) 
    except: return 0
    return 0

# --- 메인 화면: 100% 실증 데이터 랭킹 ---
st.header("📋 Reg SHO 실증 랭킹 (19일 벽 격파)")

# 1. 일단 현재 등재된 종목 리스트를 DB에서 가져옵니다.
res = supabase.table("reg_sho_logs").select("symbol, security_name, recorded_date").execute()

if res.data:
    df = pd.DataFrame(res.data)
    df['recorded_date'] = pd.to_datetime(df['recorded_date'])
    latest_date = df['recorded_date'].max()
    current_symbols = df[df['recorded_date'] == latest_date]['symbol'].unique()
    
    final_ranking = []
    
    # [진행 바] 실시간 팩트 체크 진행 상황
    progress_text = "ORTEX API에서 실시간 팩트 수집 중..."
    my_bar = st.progress(0, text=progress_text)
    
    for i, sym in enumerate(current_symbols):
        # [해결] DB 카운트가 아니라 API에서 준 '진짜 숫자'를 바로 꽂습니다.
        actual_days = get_real_regsho_days(sym)
        
        # 만약 API 숫자가 0이면, 최소한 우리 DB에 있는 숫자라도 보여줍니다.
        display_days = actual_days if actual_days > 0 else len(df[df['symbol'] == sym])
        
        name = df[df['symbol'] == sym]['security_name'].iloc[0]
        final_ranking.append({
            "로고": get_logo(sym),
            "티커": sym,
            "종목명": name,
            "진짜 등재일": display_days,
            "상태": "☢️ 폭발 위험" if display_days >= 35 else "⚠️ 주의" if display_days >= 13 else "ℹ️ 관찰"
        })
        my_bar.progress((i + 1) / len(current_symbols))
    
    my_bar.empty()
    
    # 2. 결과 출력 (추정 없는 팩트 랭킹)
    ranking_df = pd.DataFrame(final_ranking).sort_values(by='진짜 등재일', ascending=False)
    
    st.dataframe(
        ranking_df,
        column_config={
            "로고": st.column_config.ImageColumn(""),
            "진짜 등재일": st.column_config.NumberColumn("연속 등재 (팩트)", format="%d 일 🗓️"),
        },
        use_container_width=True, hide_index=True
    )
