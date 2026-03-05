import streamlit as st
import pandas as pd
import requests
from supabase import create_client

# 1. 인프라 설정
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
ORTEX_API_KEY = "9vOWMVq6.ViwuNCVtA318YnQTg2FoG3ucwEUCHmMX"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="NSD PRO: ANALYTICS", layout="wide")

# --- 데이터 호출 함수 ---
def fetch_ortex_details(ticker):
    url = f"https://api.ortex.com/v1/stocks/{ticker}/short-interest"
    headers = {"Authorization": f"Bearer {ORTEX_API_KEY}"}
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200: return resp.json()
    except: return None
    return None

# --- 사이드바 ---
with st.sidebar:
    st.title("🛡️ NSD PRO")
    menu = st.radio("메뉴", ["📈 Reg SHO 목록", "🔥 숏 스퀴즈 분석"])
    st.divider()
    st.success("✅ ORTEX 실시간 엔진 가동 중")

# --- [메뉴 1] Reg SHO 목록 ---
if menu == "📈 Reg SHO 목록":
    st.header("📋 Reg SHO 감시 리스트")
    # (기존의 깔끔한 리스트 UI 유지)
    res = supabase.table("reg_sho_logs").select("symbol, security_name, recorded_date").execute()
    if res.data:
        df = pd.DataFrame(res.data)
        df['recorded_date'] = pd.to_datetime(df['recorded_date'])
        latest_date = df['recorded_date'].max()
        ranking = []
        for sym in df[df['recorded_date'] == latest_date]['symbol'].unique():
            streak = len(df[df['symbol'] == sym])
            ranking.append({"티커": sym, "현재기록": streak, "ORTEX": f"https://ortex.com/symbol/NASDAQ/{sym}/short_interest"})
        st.dataframe(pd.DataFrame(ranking).sort_values(by="현재기록", ascending=False), use_container_width=True, hide_index=True)

# --- [메뉴 2] 🔥 숏 스퀴즈 분석 (드디어 완성!) ---
elif menu == "🔥 숏 스퀴즈 분석":
    st.header("🎯 실시간 숏 스퀴즈 정밀 분석")
    st.write("ORTEX API를 호출하여 공매도 세력의 현재 상태를 팩트 체크합니다.")
    
    target = st.text_input("분석할 티커 입력", value="BNAI").upper()
    
    if target:
        data = fetch_ortex_details(target)
        if data:
            # 1. 핵심 수치 4종 세트 (Metric)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Short Interest (%)", f"{data.get('si_pct', 0)}%", "공매도 비중")
            c2.metric("Borrow Fee (CTB)", f"{data.get('ctb_avg', 0)}%", "대여료 폭등")
            c3.metric("Utilization", f"{data.get('utilization', 0)}%", "잔여수량 없음")
            c4.metric("Days to Cover", f"{data.get('dtc', 0)}", "상환 소요기간")
            
            # 2. 시각화 (진행바)
            st.divider()
            score = (data.get('si_pct', 0) * 1.5) + (data.get('ctb_avg', 0) / 10)
            st.subheader(f"🚀 {target} 폭발 위험도: {score:.1f} / 100")
            st.progress(min(score/100, 1.0))
            
            # 3. ORTEX 차트 직접 이동
            st.link_button(f"🔗 ORTEX에서 {target} 상세 차트 보기", f"https://ortex.com/symbol/NASDAQ/{target}/short_interest")
        else:
            st.warning("ORTEX API에서 해당 종목 데이터를 찾을 수 없습니다. (유효한 티커인지 확인하세요)")
