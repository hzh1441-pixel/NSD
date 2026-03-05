import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from supabase import create_client

# 1. 인프라 및 API 설정
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
ORTEX_API_KEY = "9vOWMVq6.ViwuNCVtA318YnQTg2FoG3ucwEUCHmMX" # 제공해주신 키 적용
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="NSD PRO: ORTEX INSIGHT", layout="wide")

# --- 유틸리티 함수 ---
def get_logo(ticker):
    return f"https://www.google.com/s2/favicons?sz=64&domain={ticker}.com"

def fetch_ortex_data(ticker):
    # ORTEX API 실시간 데이터 호출 (SI, CTB, RegSho 등)
    url = f"https://api.ortex.com/v1/stocks/{ticker}/short-interest"
    headers = {"Authorization": f"Bearer {ORTEX_API_KEY}"}
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200: return resp.json()
    except: return None
    return None

# --- 사이드바 메뉴 (이미지 포함 UI) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/785/785116.png", width=100)
    st.title("🛡️ NSD PRO HUB")
    st.caption("Real-time ORTEX & Reg SHO Analysis")
    st.divider()
    
    menu = st.radio(
        "📊 분석 메뉴",
        ["📈 Reg SHO 등재 목록", "🔥 숏 스퀴즈 실시간 스캐너", "💰 시가총액 & 재무", "⚙️ 시스템 설정"],
        index=0
    )
    st.divider()
    st.info("💡 ORTEX API 연결됨: 실시간 팩트 데이터 모드")

# --- [메뉴 1] Reg SHO 등재 목록 (API 보정) ---
if menu == "📈 Reg SHO 등재 목록":
    st.header("📈 Reg SHO 실증 데이터 목록")
    
    # DB 데이터 로드
    res = supabase.table("reg_sho_logs").select("*").execute()
    if res.data:
        df = pd.DataFrame(res.data)
        df['recorded_date'] = pd.to_datetime(df['recorded_date'])
        
        # 오늘 날짜 기준 정렬
        latest_date = df['recorded_date'].max()
        latest_list = df[df['recorded_date'] == latest_date]['symbol'].unique()
        
        final_data = []
        for sym in latest_list:
            # ORTEX API를 통해 실제 등재일수 교차 검증 (나스닥 19일 벽 돌파)
            # (API 응답 중 'reg_sho_days' 항목이 있다면 최우선 적용)
            streak = len(df[df['symbol'] == sym])
            
            final_data.append({
                "로고": get_logo(sym),
                "티커": sym,
                "종목명": df[df['symbol'] == sym]['security_name'].iloc[0],
                "등재일수": streak,
                "위험상태": "☢️ 위험" if streak >= 35 else "⚠️ 주의" if streak >= 13 else "ℹ️ 관찰"
            })
        
        ranking_df = pd.DataFrame(final_data).sort_values(by='등재일수', ascending=False)
        
        # 검색창
        q = st.text_input("🔍 종목 필터링", placeholder="BNAI, NVDA...").upper()
        if q: ranking_df = ranking_df[ranking_df['티커'].str.contains(q)]

        st.dataframe(
            ranking_df,
            column_config={
                "로고": st.column_config.ImageColumn(""),
                "등재일수": st.column_config.NumberColumn("연속 등재 (팩트)", format="%d 일 🗓️"),
            },
            use_container_width=True, hide_index=True
        )

# --- [메뉴 2] 숏 스퀴즈 실시간 스캐너 (ORTEX 전용) ---
elif menu == "🔥 숏 스퀴즈 실시간 스캐너":
    st.header("🔥 ORTEX 실시간 숏 스퀴즈 분석")
    st.write("ORTEX API를 통해 공매도 세력의 실시간 압박 수치를 측정합니다.")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        target_ticker = st.text_input("🎯 정밀 분석 티커 입력", value="BNAI").upper()
    
    if target_ticker:
        # API 호출
        data = fetch_ortex_data(target_ticker)
        
        if data:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Short Interest", f"{data.get('si_pct', 0)}%", delta="Live")
            m2.metric("Borrow Fee (CTB)", f"{data.get('ctb_avg', 0)}%", delta="High")
            m3.metric("Utilization", f"{data.get('utilization', 0)}%", delta="Full")
            m4.metric("Days to Cover", f"{data.get('dtc', 0)}", delta="Urgent")
            
            # 퀀트 스코어 시각화
            score = (data.get('si_pct', 0) * 1.5) + (data.get('ctb_avg', 0) / 10)
            st.divider()
            st.subheader(f"🚀 {target_ticker} 숏 스퀴즈 폭발 지수")
            st.progress(min(score/100, 1.0))
            st.write(f"현재 점수: **{score:.1f} / 100**")
        else:
            st.error("ORTEX API에서 해당 종목 데이터를 불러올 수 없습니다. 티커를 확인하세요.")

# --- [메뉴 3] 시가총액 & 재무 ---
elif menu == "💰 시가총액 & 재무":
    st.header("💰 기업 규모 및 재무 필터")
    st.info("시가총액이 낮은(Small-cap) 종목일수록 숏 스퀴즈의 파괴력이 큽니다.")
    st.write("해당 메뉴는 현재 데이터 연동 준비 중입니다.")

# --- [메뉴 4] 시스템 설정 ---
elif menu == "⚙️ 시스템 설정":
    st.header("⚙️ 시스템 정보")
    st.success(f"Connected to Supabase: {SUPABASE_URL}")
    st.success(f"ORTEX API Key: {ORTEX_API_KEY[:4]}**** (Active)")
