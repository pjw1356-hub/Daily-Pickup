import os
import json
import requests
from bs4 import BeautifulSoup
import datetime
import sys

# 봇 토큰과 Chat ID
TOKEN = os.environ.get("TELEGRAM_TOKEN") or ""
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID") or ""

def get_realtime_stocks():
    """네이버 금융에서 실시간 거래량 상위 종목을 가져옵니다."""
    stocks = {"KOSPI": [], "KOSDAQ": []}
    
    # 0: KOSPI, 1: KOSDAQ
    for sosok in [0, 1]:
        market_type = "KOSPI" if sosok == 0 else "KOSDAQ"
        url = f"https://finance.naver.com/sise/sise_quant.naver?sosok={sosok}"
        
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 종목 테이블 찾기
            table = soup.find('table', {'class': 'type_2'})
            rows = table.find_all('tr')
            
            count = 0
            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 5: continue
                
                name_tag = cols[1].find('a')
                if name_tag:
                    name = name_tag.text.strip()
                    price = cols[2].text.strip()
                    change = cols[3].text.strip().replace('\n', '').replace('\t', '')
                    up_down = cols[3].find('img')
                    
                    # 상승/하락 기호 표시
                    prefix = ""
                    if up_down:
                        if 'up' in up_down.get('src', ''): prefix = "🔺"
                        elif 'down' in up_down.get('src', ''): prefix = "🔻"
                    
                    stocks[market_type].append({
                        "name": name,
                        "price": price,
                        "change": f"{prefix}{change}"
                    })
                    count += 1
                    if count >= 10: break # 상위 10개만
                    
        except Exception as e:
            print(f"{market_type} 데이터를 가져오는 중 에러 발생: {e}")
            
    return stocks["KOSPI"], stocks["KOSDAQ"]

def make_message(kospi, kosdaq):
    now = datetime.datetime.now() + datetime.timedelta(hours=9) # KST 기준
    date_str = now.strftime("%Y년 %m월 %d일 %H:%M")
    
    msg = f"🚀 <b>[Dayily Pickup] 실시간 주식 보고</b> 🚀\n"
    msg += f"📅 일시: {date_str}\n\n"
    
    msg += "🔴 <b>KOSPI 거래량 상위</b>\n"
    if not kospi:
        msg += "- 데이터를 가져오지 못했습니다.\n"
    for s in kospi:
        msg += f"- {s['name']}: {s['price']}원 ({s['change']})\n"
        
    msg += "\n🔵 <b>KOSDAQ 거래량 상위</b>\n"
    if not kosdaq:
        msg += "- 데이터를 가져오지 못했습니다.\n"
    for s in kosdaq:
        msg += f"- {s['name']}: {s['price']}원 ({s['change']})\n"
        
    msg += "\n✨ 실시간 거래량 기반 추천입니다.\n성공 투자를 기원합니다! 💰"
    return msg

def send_message(text):
    if not TOKEN or not CHAT_ID:
        print("❌ 에러: TELEGRAM_TOKEN 또는 TELEGRAM_CHAT_ID가 설정되지 않았습니다.")
        sys.exit(1)

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("🎉 추천 종목 전송 성공!")
        else:
            print(f"❌ 전송 실패: {response.status_code} {response.text}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("실시간 주식 데이터를 가져오는 중...")
    kospi, kosdaq = get_realtime_stocks()
    
    if kospi or kosdaq:
        message = make_message(kospi, kosdaq)
        print("메시지를 전송합니다...")
        send_message(message)
    else:
        print("❌ 전송할 데이터가 없습니다.")
