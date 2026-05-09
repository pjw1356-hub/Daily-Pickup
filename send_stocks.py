import urllib.request
import urllib.parse
import json
import re
import os

# 봇 토큰과 Chat ID (깃허브 비밀금고에서 읽어오되, 없으면 기본값 사용!)
TOKEN = os.environ.get("TELEGRAM_TOKEN") or "8737498988:AAFOAzVzqjUOM4hqn6Juzbc5CdQTyasqw6o"
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID") or "6552955887"

def get_stocks_from_js():
    """app.js 파일에서 종목 정보를 쏙쏙 뽑아오는 함수입니다."""
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'app.js')
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        kospi_match = re.search(r'const kospiData\s*=\s*\[(.*?)\];', content, re.DOTALL)
        kosdaq_match = re.search(r'const kosdaqData\s*=\s*\[(.*?)\];', content, re.DOTALL)
        
        def parse_stocks(text):
            stocks = []
            items = re.findall(r'\{(.*?)\}', text, re.DOTALL)
            for item in items:
                name = re.search(r'name:\s*"(.*?)"', item)
                price = re.search(r'price:\s*"(.*?)"', item)
                is_new = "isNew: true" in item
                
                if name and price:
                    stocks.append({
                        "name": name.group(1),
                        "price": price.group(1),
                        "is_new": is_new
                    })
            return stocks

        kospi_stocks = parse_stocks(kospi_match.group(1)) if kospi_match else []
        kosdaq_stocks = parse_stocks(kosdaq_match.group(1)) if kosdaq_match else []
        
        print(f"KOSPI 종목 수: {len(kospi_stocks)}개, KOSDAQ 종목 수: {len(kosdaq_stocks)}개")
        return kospi_stocks, kosdaq_stocks
        
    except Exception as e:
        print(f"파일을 읽는 중 에러가 발생했습니다: {e}")
        return [], []

def make_message(kospi, kosdaq):
    msg = "📊 <b>[Dayily Pickup] 오늘의 추천 종목</b> 📊\n\n"
    
    msg += "🔴 <b>KOSPI 추천 종목</b>\n"
    if not kospi:
        msg += "- 종목을 가져오지 못했습니다.\n"
    for s in kospi:
        new_tag = " [🔥NEW]" if s['is_new'] else ""
        msg += f"- {s['name']} ({s['price']}){new_tag}\n"
        
    msg += "\n🔵 <b>KOSDAQ 추천 종목</b>\n"
    if not kosdaq:
        msg += "- 종목을 가져오지 못했습니다.\n"
    for s in kosdaq:
        new_tag = " [🔥NEW]" if s['is_new'] else ""
        msg += f"- {s['name']} ({s['price']}){new_tag}\n"
        
    msg += "\n🚀 오늘도 성공 투자 하세요! 🚀"
    return msg

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": int(CHAT_ID),
        "text": text,
        "parse_mode": "HTML"
    }
    data = json.dumps(payload).encode("utf-8")
    
    try:
        req = urllib.request.Request(url, data=data)
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        with urllib.request.urlopen(req) as response:
            print("🎉 추천 종목 전송 성공!")
    except Exception as e:
        print(f"❌ 전송 실패: {e}")
        import sys
        sys.exit(1)

if __name__ == "__main__":
    print("추천 종목을 읽어오는 중...")
    kospi, kosdaq = get_stocks_from_js()
    
    if kospi or kosdaq:
        message = make_message(kospi, kosdaq)
        print("메시지를 전송합니다...")
        send_message(message)
    else:
        print("❌ 전송할 종목이 없습니다.")
