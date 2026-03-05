# --- [메뉴 2] 🔥 숏 스퀴즈 분석 (실시간 팩트 체크실) ---
elif menu == "🔥 숏 스퀴즈 분석":
    st.header("🎯 ORTEX 실시간 정밀 분석")
    st.write("우리 앱의 19일 기록을 넘어, ORTEX가 가진 실시간 수치로 승부처를 찾습니다.")
    
    # 분석할 티커 입력
    target = st.text_input("🔍 분석할 티커 입력 (예: BNAI, AMZD)", value="BNAI").upper()
    
    if target:
        # ORTEX API 호출
        data = fetch_ortex_details(target) # 이전에 만든 API 호출 함수 활용
        
        if data:
            # 1. 월가 프로들이 보는 핵심 지표 4가지
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Short Interest", f"{data.get('si_pct', 0)}%", "공매도 비중")
            c2.metric("Borrow Fee (CTB)", f"{data.get('ctb_avg', 0)}%", "이자 부담")
            c3.metric("Utilization", f"{data.get('utilization', 0)}%", "빌릴 주식 없음")
            c4.metric("DTC", f"{data.get('dtc', 0)}", "탈출 소요기간")
            
            # 2. 팩트 기반 폭발 점수
            st.divider()
            score = (data.get('si_pct', 0) * 1.5) + (data.get('ctb_avg', 0) / 10)
            st.subheader(f"🚀 {target} 스퀴즈 에너지 점수: {score:.1f} / 100")
            st.progress(min(score/100, 1.0))
            
            # 3. 상세 페이지 점프
            st.link_button(f"🔗 {target} ORTEX 상세 페이지 열기", f"https://ortex.com/symbol/NASDAQ/{target}/short_interest")
        else:
            st.warning("현재 ORTEX API 연결 상태를 확인 중이거나 해당 티커의 실시간 데이터가 없습니다.")
