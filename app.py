import streamlit as st
import pandas as pd
from supabase import create_client

# 1. 인프라 설정
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 페이지 설정 (와이드 모드)
st.set_page_config(page_title="NSD PRO: STRATEGY HUB", layout="wide")

# 로고 함수
def get_logo(ticker):
    return f"https://www.google.com/s2/favicons?sz=64&domain={ticker}.com"

# --- 사이드바: 깔끔한 메뉴 ---
with st.sidebar:
    st.title("🛡️ NSD PRO")
    st.subheader("Reg SHO 감시 센터")
    st.divider()
    st.info("💡 19일 표시 종목은 '현재 DB 최대치'를 의미합니다. 실제 일수는 ORTEX 버튼으로 확인하세요.")

# --- 메인 화면 ---
st.header("📋 실시간 Reg SHO 감시 리스트")

# DB 데이터 로드
res = supabase.table("reg_sho_logs").select("symbol, security_name, recorded_date").execute()

if res.data:
    df = pd.DataFrame(res.data)
    df['recorded_date'] = pd.to_datetime(df['recorded_date'])
    latest_date = df['recorded_date'].max()
    
    # 등재 일수 계산 (현재 DB 기준)
    ranking = []
    for sym in df[df['recorded_date'] == latest_date]['symbol'].unique():
        streak = len(df[df['symbol'] == sym])
        name = df[df['symbol'] == sym]['security_name'].iloc[0]
        
        # ORTEX 직접 이동 링크 생성
        ortex_url = f"https://ortex.com/symbol/NASDAQ/{sym}/short_interest"
        
        ranking.append({
            "로고": get_logo(sym),
            "티커": sym,
            "종목명": name,
            "DB 기록(일)": streak,
            "상태": "🔥 집중감시" if streak >= 19 else "ℹ️ 관찰",
            "ORTEX": ortex_url
        })

    final_df = pd.DataFrame(ranking).sort_values(by="DB 기록(일)", ascending=False)

    # [UI 핵심] 표 형식 정돈
    st.dataframe(
        final_df,
        column_config={
            "로고": st.column_config.ImageColumn(""),
            "티커": st.column_config.TextColumn("티커", width="small"),
            "DB 기록(일)": st.column_config.NumberColumn("현재 기록", format="%d일"),
            "ORTEX": st.column_config.LinkColumn("팩트체크 바로가기", display_text="ORTEX 열기 🔗")
        },
        use_container_width=True, hide_index=True
    )

# --- 하단 가이드 ---
st.divider()
st.markdown("""
### **🚀 투자 전략 가이드**
1.  **현재 기록 19일**인 종목을 먼저 확인하세요. (이들은 최소 19일 이상 등재된 정예병입니다.)
2.  오른쪽 **'ORTEX 열기'** 버튼을 누르세요.
3.  ORTEX 웹사이트에서 **'Days on Reg SHO'**의 진짜 숫자와 **Short Interest %**를 최종 확인 후 진입하세요.
""")
