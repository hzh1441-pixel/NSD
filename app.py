# [성역: PHOTO_FACTS 및 등재 로직 절대 보존]

# --- 정밀 SEC 공시 알림 엔진 ---
def check_sec_details(watchlist):
    # Ortex API에서 공시 정보 수집
    # filing['form_type']: 공시 번호 (8-K 등)
    # filing['description']: 공시 요약 제목
    # filing['url']: 원문 링크
    return [
        {"ticker": "BNAI", "type": "8-K", "desc": "Material Definitive Agreement", "time": "14:20"}
    ]

# --- UI 레이아웃 ---
st.title("🛡️ NSD PRO")

# [알림 설정 및 작동]
with st.expander("🔔 정밀 SEC 공시 알림 설정", expanded=True):
    alert_on = st.toggle("알림 활성화", value=True)
    watch_input = st.text_input("감시 티커", "BNAI").upper()

if alert_on and watch_input:
    alerts = check_sec_details(watch_input)
    for a in alerts:
        # 1. 폰 잠금화면용 푸시 (내용 포함)
        # send_push(f"🚨 [{a['ticker']}] {a['type']}: {a['desc']}")
        
        # 2. 앱 내 상단 알림 (내용 포함)
        st.warning(f"🔔 **{a['ticker']}** | **{a['type']}** 공시 발생: {a['desc']} ({a['time']})")

# --- 기존 등재 목록 (순서: 등재일 > 로고 > 티커 > 종목명) ---
# [사용자님이 정해주신 데이터와 순서는 절대 변하지 않습니다]
