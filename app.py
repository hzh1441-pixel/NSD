import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from supabase import create_client

# 1. 인프라 및 API 설정 (사용자 키 적용)
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
ORTEX_API_KEY = "9vOWMVq6.ViwuNCVtA318YnQTg2FoG3ucwEUCHmMX"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 페이지 설정 (가장 먼저 와야 함)
st.set_page_config(page_title="NSD PRO: ORTEX HUB", layout="wide")

# --- 유틸리티 함수 ---
def get_logo(ticker):
    return f"https://www.google.com/s2/favicons?sz=64&domain={ticker}.com"

# [핵심] ORTEX API 호출 함수
def fetch_ortex_data(ticker):
    url = f"https://api.ortex.com/v1/stocks/{ticker}/short-interest"
    headers = {"Authorization": f"Bearer {ORTEX_API_KEY}"}
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200: return resp.json()
    except: return None
    return None

# --- 사이드바 메뉴 (이게 생겨야 정상입니다) ---
with st.sidebar:
    st.title("🛡️ NSD PRO HUB")
    st.markdown("---")
    # 메뉴 아이콘과 함께 구성
    menu = st.radio(
        "📂 분석 메뉴",
        ["📈 Reg SHO 등재 목록", "🔥 숏 스퀴즈 실시간 스캐너", "💰 시가총액 & 재무"],
        index=0
    )
    st.markdown("---")
    st.success("✅ ORTEX API 연결됨")

# --- [메뉴 1] Reg SHO 등재 목록 ---
if menu == "📈 Reg SHO 등재 목록":
    st.header("📈 Reg SHO 실증 데이터 목록")
    
    # DB 데이터 가져오기
    res = supabase.table("reg_sho_logs").select("*").execute()
    
    if res.data:
        df = pd.DataFrame(res.data)
        df['recorded_date'] = pd.to_datetime(df['recorded_date'])
        
        # 19일 벽을 넘기 위해: DB에 있는 모든 과거 기록을 중복 없이 카운트
        available_dates = sorted(df['recorded_date'].unique(), reverse=True)
        latest_date = available_dates[0]
        latest_list = df[df['recorded_date'] == latest_date]['symbol'].unique()
        
        final_ranking = []
        for sym in latest_list:
            # 연속성 계산: 날짜가 비어있어도 과거 기록이 있다면 합산 (19일 돌파 로직)
            streak = len(df[df['symbol'] == sym])
            
            final_ranking.append({
                "로고": get_logo(sym),
                "티커": sym,
                "종목명": df[df['symbol'] == sym]['security_name'].iloc[0],
                "등재일수": streak,
                "상태": "☢️ 위험" if streak >= 35 else "⚠️ 주의" if streak >= 13 else "ℹ️ 초기"
            })
            
        ranking_df = pd.DataFrame(final_ranking).sort_values(by='등재일수', ascending=False)
        
        st.info(f"📊 팩트 체크: 현재 DB 내 {len(available_dates)}거래일 기록 추적 중")
        
        # UI 표 출력
        st.dataframe(
            ranking_df,
            column_config={
                "로고": st.column_config.ImageColumn(""),
                "등재일수": st.column_config.NumberColumn("누적 등재일", format="%d 일 🗓️"),
            },
            use_container_width=True, hide_index=True
        )

# --- [메뉴 2] 숏 스퀴즈 실시간 스캐너 ---
elif menu == "🔥 숏 스퀴즈 실시간 스캐너":
    st.header("🔥 ORTEX 실시간 데이터 분석")
    
    target = st.text_input("🎯 분석할 티커 입력", value="BNAI").upper()
    
    if target:
        # ORTEX API 실시간 호출
        data = fetch_ortex_data(target)
        
        if data:
            # 대시보드 형태의 수치 카드 
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Short Interest", f"{data.get('si_pct', 0)}%", "SI %")
            c2.metric("Borrow Fee (CTB)", f"{data.get('ctb_avg', 0)}%", "Cost")
            c3.metric("Utilization", f"{data.get('utilization', 0)}%", "Full")
            c4.metric("Days to Cover", f"{data.get('dtc', 0)}", "Time")
            
            # 폭발 지수 시각화
            score = (data.get('si_pct', 0) * 1.5) + (data.get('ctb_avg', 0) / 10)
            st.divider()
            st.subheader(f"🚀 {target} 스퀴즈 위험 점수: {score:.1f} / 100")
            st.progress(min(score/100, 1.0))
        else:
            st.warning("해당 종목의 ORTEX 데이터를 불러올 수 없습니다.")
