import streamlit as st
import pandas as pd
import requests
from supabase import create_client

# 1. 인프라 설정
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
ORTEX_API_KEY = "9vOWMVq6.ViwuNCVtA318YnQTg2FoG3ucwEUCHmMX"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="NSD PRO", layout="wide")

# --- 사이드바 메뉴 ---
with st.sidebar:
    st.title("🛡️ NSD PRO")
    menu = st.radio("메뉴 선택", ["📈 Reg SHO 목록", "🔥 숏 스퀴즈 분석"])
    st.divider()
    st.success("✅ ORTEX 엔진 가동 중")

# --- [메뉴 1] Reg SHO 목록 ---
if menu == "📈 Reg SHO 목록":
    st.header("📋 Reg SHO 감시 리스트")
    res = supabase.table("reg_sho_logs").select("symbol, security_name, recorded_date").execute()
    if res.data:
        df = pd.DataFrame(res.data)
        df['recorded_date'] = pd.to_datetime(df['recorded_date'])
        latest_date = df['recorded_date'].max()
        ranking = []
        for sym in df[df['recorded_date'] == latest_date]['symbol'].unique():
            streak = len(df[df['symbol'] == sym])
            ranking.append({
                "티커": sym, 
                "DB기록": f"{streak}일", 
                "ORTEX링크": f"https://ortex.com/symbol/NASDAQ/{sym}/short_interest"
            })
        st.dataframe(pd.DataFrame(ranking).sort_values(by="DB기록", ascending=False), use_container_width=True, hide_index=True)

# --- [메뉴 2] 🔥 숏 스퀴즈 분석 (드디어 기능을 채웠습니다) ---
elif menu == "🔥 숏 스퀴즈 분석":
    st.header("🎯 실시간 숏 스퀴즈 정밀 분석")
    st.write("분석하고 싶은 티커를 입력하면 ORTEX의 실시간 수치를 가져옵니다.")
    
    target = st.text_input("티커 입력 (예: BNAI)", value="BNAI").upper()
    
    if target:
        url = f"https://api.ortex.com/v1/stocks/{target}/short-interest"
        headers = {"Authorization": f"Bearer {ORTEX_API_KEY}"}
        try:
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                # 화면에 큼직하게 숫자 띄우기
                c1, c2, c3 = st.columns(3)
                c1.metric("공매도 잔고 (SI%)", f"{data.get('si_pct', 0)}%")
                c2.metric("대여료 (CTB)", f"{data.get('ctb_avg', 0)}%")
                c3.metric("이용률", f"{data.get('utilization', 0)}%")
                
                st.divider()
                st.link_button(f"🔗 ORTEX에서 {target} 진짜 등재일 확인하기", f"https://ortex.com/symbol/NASDAQ/{target}/short_interest")
            else:
                st.error("해당 종목의 실시간 데이터를 찾을 수 없습니다.")
        except:
            st.error("API 연결 중 오류가 발생했습니다.")
