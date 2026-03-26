import requests
import time
import datetime
import os
import xml.etree.ElementTree as ET
from supabase import create_client

# --- [환경 설정: 건드릴 필요 없음] ---
TOKEN = "8306599736:AAHwT_jhT9DHJqdWubOQoL1JuNlBbMjswGw"
CHAT_ID = "8182795005"
DB_FILE = "sent_filings.txt"
SEC_URL = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&owner=include&output=atom"
HEADERS = {'User-Agent': 'NSD_PRO_Bot (my-email@example.com)'} 

SUPABASE_URL = "https://rqpazefumujrwbddymly.supabase.co"
SUPABASE_KEY = "sb_publishable_dwWER9BMd3z_zq_m5JevEA_A-rUqZFz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML", "disable_web_page_preview": True}
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass

def get_watchlist_from_streamlit():
    """스트림릿에서 저장한 user_config 테이블의 watchlist 컬럼을 그대로 읽어옵니다."""
    try:
        res = supabase.table('user_config').select('watchlist').eq('id', 1).execute()
        if res.data and 'watchlist' in res.data[0]:
            tickers_str = res.data[0]['watchlist']
            if tickers_str:
                return [t.strip().upper() for t in tickers_str.split(',') if t.strip()]
        return []
    except Exception as e:
        print(f"스트림릿 설정 연동 대기 중... ({e})")
        return []

def check_sec():
    if not os.path.exists(DB_FILE):
        open(DB_FILE, 'w').close()

    # 최초 실행 시 스트림릿 연동 상태 확인 메시지 발송
    try:
        initial_list = get_watchlist_from_streamlit()
        current_tickers = ", ".join(initial_list) if initial_list else "등록된 종목 없음"
        send_telegram(f"✅ <b>[NSD PRO] 시스템 가동 준비 완료</b>\n현재 스트림릿에 설정된 감시 종목: {current_tickers}")
    except:
        pass

    while True:
        now = datetime.datetime.now()
        
        # 한국 시간 09:00 생존 보고
        if now.hour == 0 and now.minute == 0 and now.second < 25:
            current_list = get_watchlist_from_streamlit()
            current_tickers = ", ".join(current_list) if current_list else "없음"
            send_telegram(f"🚀 <b>[NSD PRO]</b> 시스템 정상 가동 중 (정기 보고)\n감시 중: {current_tickers}")
            time.sleep(30)

        try:
            # 1. 20초마다 스트림릿의 최신 설정을 무조건 새로 읽어옴
            watchlist = get_watchlist_from_streamlit()
            
            if not watchlist:
                time.sleep(20)
                continue # 스트림릿에 입력한 종목이 없으면 대기

            # 2. SEC 공시 가져오기
            response = requests.get(SEC_URL, headers=HEADERS, timeout=15)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                
                for entry in root.findall('atom:entry', ns):
                    title_el = entry.find('atom:title', ns)
                    if title_el is None: continue
                    title = title_el.text
                    
                    link_el = entry.find('atom:link', ns)
                    link = link_el.attrib['href'] if link_el is not None else SEC_URL
                    
                    id_el = entry.find('atom:id', ns)
                    if id_el is None: continue
                    filing_id = id_el.text
                    
                    with open(DB_FILE, 'r') as f:
                        sent_ids = f.read().splitlines()
                    
                    if filing_id not in sent_ids:
                        for stock in watchlist:
                            if stock in title.upper():
                                msg = f"🚨 <b>[SEC 신규 공시 발견!]</b>\n\n📌 <b>종목:</b> {stock}\n📄 <b>종류:</b> {title.split(' - ')[0]}\n🔗 <a href='{link}'>문서 바로보기</a>"
                                send_telegram(msg)
                                with open(DB_FILE, 'a') as f:
                                    f.write(filing_id + "\n")
                                break
        except Exception as e:
            pass # 에러가 나도 절대 멈추지 않고 다음 20초 뒤에 재시도
        
        time.sleep(20)

if __name__ == "__main__":
    check_sec()
