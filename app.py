import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime, timedelta
from supabase import create_client

# 1. 인프라 설정
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="NSD PRO HUB", layout="wide")

# 2. 데이터 수집 엔진 (나스닥 + SEC 역추적 로직)
def auto_deep_sync():
    # 최근 90일치 날짜 생성
    today = datetime.now()
    dates_to_check = [(today - timedelta(days=i)).strftime('%Y%m%d') for i in range(90)]
    
    # 이미 DB에 있는 날짜들 확인 (중복 작업 방지)
    existing_res = supabase.table("reg_sho_logs").select("recorded_date").execute()
    existing_dates = set()
    if existing_res.data:
        existing_dates = {d['recorded_date'].replace('-', '') for d in existing_res.data}

    new_data_count = 0
    for d_str in dates_to_check:
        if d_str in existing_dates: continue # 이미 있으면 패스
        
        url = f"https://www.nasdaqtrader.com/dynamic/symdir/regsho/nasdaqth{d_str}.txt"
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                df = pd.read_csv(url, sep='|')[:-1]
                df.columns = df.columns.str.strip()
                for _, row in df.iterrows():
                    data = {
                        "symbol": row['Symbol'],
                        "security_name": row['Security Name'],
                        "recorded_date": f"{d_str[:4]}-{d_str[4:6]}-{d_str[6:]}"
                    }
                    supabase.table("reg_sho_logs").upsert(data).execute()
                new_data_count += 1
                if new_data_count > 5: break # 한 번에 너무 많이 가져오면 차단될 수 있으니 점진적 추가
        except: continue
    return True

# --- [핵심] 무인 자동 복구 실행 ---
if "deep_synced" not in st.session_state:
    with st.status("🔍 과거 데이터 무결성 검사 및 자동 복구 중...", expanded=False):
        auto_deep_sync()
    st.session_state["deep_synced"] = True

# --- 메인 화면: Reg SHO 등재 목록 ---
with st.sidebar:
    st.title("📂 NSD PRO HUB")
    menu = st.radio("메뉴 선택", ["Reg SHO 등재 목록", "주요 공시(SEC)", "시가총액/재무"])

if menu == "Reg SHO 등재 목록":
    st.header("📋 Reg SHO 등재 목록")
    
    # 전체 기록 로드 (연속성 분석용)
    res = supabase.table("reg_sho_logs").select("symbol, security_name, recorded_date").execute()

    if res.data:
        df = pd.DataFrame(res.data)
        df['recorded_date'] = pd.to_datetime(df['recorded_date'])
        
        # 유효 영업일 리스트 (데이터가 존재하는 날짜들만)
        available_dates = sorted(df['recorded_date'].unique(), reverse=True)
        latest_date = available_dates[0]
        latest_list = df[df['recorded_date'] == latest_date]
        
        final_ranking = []
        for _, row in latest_list.iterrows():
            sym = row['symbol']
            # [연속성 보정 로직] DB에 데이터가 있는 날짜 순서대로 거꾸로 올라가며 체크
            streak = 0
            sym_dates = set(df[df['symbol'] == sym]['recorded_date'])
            for d in available_dates:
                if d in sym_dates: streak += 1
                else: break
            
            final_ranking.append({'티커': sym, '종목명': row['security_name'], '등재일수': streak})

        ranking_df = pd.DataFrame(final_ranking).sort_values(by='등재일수', ascending=False)

        # 상태 및 마지노선 분석
        def get_status(days):
            if days >= 40: return "☢️ 최종 마지노선 돌파"
            elif days >= 35: return "🔥 청산 임박 (35일+)"
            elif days >= 13: return "⚠️ 의무 구간"
            else: return "ℹ️ 초기 단계"
        ranking_df['상태'] = ranking_df['등재일수'].apply(get_status)

        st.info(f"📊 **데이터 무결성 리포트**: 총 {len(available_dates)}거래일 기록 추적 중 (최종 업데이트: {latest_date.strftime('%Y-%m-%d')})")
        
        search_query = st.text_input("🔍 종목 필터링", placeholder="티커 입력").upper()
        if search_query:
            ranking_df = ranking_df[ranking_df['티커'].str.contains(search_query)]

        st.dataframe(ranking_df, use_container_width=True, hide_index=True)
