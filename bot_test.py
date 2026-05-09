import urllib.request
import urllib.parse
import json

# 아까 찾은 봇 토큰과 Chat ID입니다!
TOKEN = "8737498988:AAFOAzVzqjUOM4hqn6Juzbc5CdQTyasqw6o"
CHAT_ID = "6552955887"
MESSAGE = "안녕하세요! 코부장의 도움으로 봇이 살아났습니다! 🚀"

def send_message():
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    # 보낼 데이터를 JSON 형식으로 설정
    payload = {
        "chat_id": int(CHAT_ID),
        "text": MESSAGE
    }
    data = json.dumps(payload).encode("utf-8")
    
    try:
        # 요청 보내기 (JSON 형식 명시)
        req = urllib.request.Request(url, data=data)
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        with urllib.request.urlopen(req) as response:
            result = response.read().decode("utf-8")
            print("=========================================")
            print("🎉 메시지 전송 성공! 스마트폰을 확인해 보세요! 📱")
            print("=========================================")
    except Exception as e:
        print("=========================================")
        print(f"❌ 에러가 발생했습니다: {e}")
        if hasattr(e, 'read'):
            try:
                error_details = e.read().decode("utf-8")
                print(f"💡 상세 에러 내용: {error_details}")
            except:
                pass
        print("=========================================")

if __name__ == "__main__":
    print("봇을 실행합니다...")
    send_message()
