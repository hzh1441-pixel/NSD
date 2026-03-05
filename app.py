import time
import requests
from datetime import datetime
from supabase import create_client

# ==========================================
# 1. 인프라 설정
# ==========================================
SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
TELEGRAM_TOKEN = "8306599736:AAHwT_jhT9DHJqdWubOQoL1JuNlBbMjswGw"
CHAT_ID = "8182795005"

HEADERS = {'User-Agent': 'NSD_PRO_Worker/1.0 (contact@example.com)'}

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
sent_filings = set()
cik_map = {}
is_first_run = True

def send_telegram(message):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                      data={"chat_id": CHAT_ID, "text": message}, timeout=5)
    except Exception as e:
        print(f"텔레그램 발송 실패: {e}")

# ==========================================
# 2. CIK(SEC 고유번호) 매핑 데이터 로드
# ==========================================
def refresh_cik_map():
    global cik_map
    try:
        print("SEC 종목 데이터 불러오는 중...")
        res = requests.get("https://www.sec.gov/files/company_tickers.json", headers=HEADERS, timeout=10)
        if res.status_code == 200:
            cik_map = {item['ticker']: str(item['cik_str']) for item in res.json().values()}
            print(f"✅ 나스닥 {len(cik_map)}개 종목 CIK 데이터 로드 완료")
    except Exception as e:
        print(f"❌ CIK 로드 실패: {e}")

# ==========================================
# 3. 24시간 실시간 감시 로직
# ==========================================
def check_and_alert():
    global is_first_run
    try:
        # DB에서 앱에서 저장한 리스트 읽어오기
        res = supabase.table("user_config").select("*").eq("id", 1).execute()
        if not res.data or not res.data[0]['alert_enabled']: 
            return
        
        watch_str = res.data[0]['watchlist']
        if not watch_str:
            return
            
        watchlist = [t.strip().upper() for t in watch_str.split(",") if t.strip()]
        
        # 🔥 [핵심] 출근 보고: 프로그램 시작 시 딱 한 번 폰으로 알림 쏘기
        if is_first_run:
            send_telegram(f"🤖 [NSD PRO 백그라운드 가동 시작]\n\n앱이 꺼져 있어도 아래 종목의 공시를 24시간 감시합니다.\n📌 현재 감시 목록: {watch_str}")
        
        for ticker in watchlist:
            cik = cik_map.get(ticker)
            if not cik: continue
            
            url = f"https://data.sec.gov/submissions/CIK{cik.zfill(10)}.json"
            response = requests.get(url, headers=HEADERS, timeout=10)
            
            if response.status_code == 200:
                recent = response.json().get('filings', {}).get('recent', {})
                if not recent: continue
                
                f_id = recent['accessionNumber'][0]
                if f_id not in sent_filings:
                    # 첫 실행 시 과거 공시 스팸 방지 (출근 보고만 하고 넘어감)
                    if not is_first_run:
                        msg = (f"🚨 [{ticker}] 신규 SEC 공시 포착!\n\n"
                               f"📌 종류: {recent['form'][0]}\n"
                               f"📄 내용: {recent['primaryDocDescription'][0]}\n"
                               f"🔗 https://www.sec.gov/edgar/browse/?CIK={cik}")
                        send_telegram(msg)
                        print(f"[{datetime.now()}] {ticker} 알림 전송 완료")
                    
                    sent_filings.add(f_id)
                    
        is_first_run = False 
        
    except Exception as e:
        print(f"[{datetime.now()}] 모니터링 중 에러: {e}")

# ==========================================
# 4. 무한 루프 실행 (앱이 꺼져도 여기서 계속 돎)
# ==========================================
print(f"🛡️ NSD PRO 지하 감시병 가동 (시간: {datetime.now()})")
refresh_cik_map() 

while True:
    check_and_alert()
    time.sleep(60) # 1분마다 SEC 확인
