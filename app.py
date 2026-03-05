import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from supabase import create_client

# 1. 인프라 설정
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="NSD PRO HUB", layout="wide")

# 2. 데이터 수집 함수
def sync_data(target_date_str):
    url = f"https://www.nasdaqtrader.com/dynamic/symdir/regsho/nasdaqth{target_date_str}.txt"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            df = pd.read_csv(url, sep='|')[:-1]
            df.columns = df.columns.str.strip()
            for _, row in df.iterrows():
                data = {
                    "symbol": row['Symbol'],
                    "security_name": row['Security Name'],
                    "recorded_date": f"{target_date_str[:4]}-{target_date_str[4:6]}-{target_date_str[6:]}"
                }
                supabase.table("reg_sho_logs").upsert(data).execute()
            return True
    except: pass
    return False

# --- 사이드바 메뉴 구성 ---
with st.sidebar:
    st.title("📂 NSD PRO HUB")
    menu = st.radio(
        "메뉴 선택",
        ["Reg SHO 등재 목록", "주요 공시(SEC)", "시가총액/재무", "설정"]
    )
    st.divider()
    if st.button("🔄 과거 90일 강제 동기화"):
        with st.spinner("데이터 복구 중..."):
            for i in range(90):
                d = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
                sync_data(d)
        st.success("90일 데이터 확보 완료!")

# --- 1. Reg SHO 등재 목록 메인 화면 ---
if menu == "Reg SHO 등재 목록":
    # 접속 시 자동 동기화 (최근 5일)
    if "first_run" not in st.session_state:
        with st.status("📡 최신 데이터 확인 중...", expanded=False) as status:
            for i in range(5):
                target_d = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
                sync_data(target_d)
            status.update(label="✅ 동기화 완료", state="complete")
        st.session_state["first_run"] = True

    st.header("📋 Reg SHO 등재 목록")

    res = supabase.table("reg_sho_logs").select("symbol, security_name, recorded_date").execute()

    if res.data:
        df = pd.DataFrame(res.data)
        df['recorded_date'] = pd.to_datetime(df['recorded_date'])
        
        available_dates = sorted(df['recorded_date'].unique(), reverse=True)
        latest_date = available_dates[0]
        latest_list = df[df['recorded_date'] == latest_date]
        
        final_ranking = []
        for _, row in latest_list.iterrows():
            sym = row['symbol']
            name = row['security_name']
            sym_dates = set(df[df['symbol'] == sym]['recorded_date'])
            
            streak = 0
            for d in available_dates:
                if d in sym_dates: streak += 1
                else: break
            final_ranking.append({'symbol': sym, '종목명': name, '등재일수': streak})

        ranking_df = pd.DataFrame(final_ranking).sort_values(by='등재일수', ascending=False)

        # 40일 마지노선 상태 분류
        def get_status(days):
            if days >= 40: return "☢️ 최종 마지노선"
            elif days >= 35: return "🔥 청산 임박"
            elif days >= 13: return "⚠️ 의무 구간"
            else: return "ℹ️ 초기 단계"
        ranking_df['상태'] = ranking_df['등재일수'].apply(get_status)

        st.info(f"📅 기준일: {latest_date.strftime('%Y-%m-%d')} | 등재 종목: {len(ranking_df)}개")

        # 검색 기능
        search_query = st.text_input("🔍 종목 필터링", placeholder="티커를 입력하세요").upper()
        if search_query:
            ranking_df = ranking_df[ranking_df['symbol'].str.contains(search_query)]

        st.dataframe(
            ranking_df,
            column_config={
                "symbol": "티커",
                "등재일수": st.column_config.NumberColumn("연속 등재일수", format="%d 일 🗓️")
            },
            use_container_width=True, hide_index=True
        )
    else:
        st.warning("데이터가 없습니다. 사이드바에서 동기화를 실행하세요.")

# --- 2. 주요 공시 메뉴 (준비 중) ---
elif menu == "주요 공시(SEC)":
    st.header("🗞️ 주요 공시(SEC)")
    st.write("해당 메뉴는 현재 준비 중입니다. (EDGAR API 연동 예정)")

# --- 3. 시가총액/재무 메뉴 (준비 중) ---
elif menu == "시가총액/재무":
    st.header("💰 시가총액/재무 정보")
    st.write("해당 메뉴는 현재 준비 중입니다. (yfinance 연동 예정)")

# --- 4. 설정 메뉴 ---
elif menu == "설정":
    st.header("⚙️ 앱 설정")
    st.write(f"Supabase URL: {SUPABASE_URL}")
    st.write("버전: v1.2 (Auto-Sync)")
