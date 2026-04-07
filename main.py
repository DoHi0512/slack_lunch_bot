import os
import requests
from bs4 import BeautifulSoup
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def get_web_data():
    url = "https://m.pusan.ac.kr/ko/meals?current=yangsan"
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        
        target_strong = None
        all_blue_texts = soup.find_all('strong', class_='blue_text')
        
        for st in all_blue_texts:
            if "정식-5,000" in st.get_text():
                target_strong = st
                break
        
        if target_strong:

            next_p = target_strong.find_next_sibling('p')
            
            if next_p:
          
                span_element = next_p.find('span')
                if span_element:
                    span_text = span_element.get_text(strip=True)
        
                    span_text = span_text.replace('\t', '').replace('\r', '')
                    return f"오늘의 점심\n\n{span_text}"
                else:
                    return "❌ 식단 내용(span)이 비어있습니다."
            else:
                return "❌ 식단 내용(p 태그)을 찾을 수 없습니다."
        else:
            return "❌ '정식-5,000' 메뉴를 찾을 수 없습니다. (식단이 없는 날일 수 있습니다.)"
            
    except Exception as e:
        return f"❌ 크롤링 오류 발생: {e}"

def send_slack_message(message):
    slack_token = os.environ.get('SLACK_TOKEN')
    channel_id = "C0APB4DT1K3" 
    
    if not slack_token:
        print("에러: SLACK_TOKEN 환경변수가 설정되지 않았습니다.")
        return

    client = WebClient(token=slack_token)
    
    try:
        client.chat_postMessage(channel=channel_id, text=message)
        print("슬랙 메시지 전송 성공!")
    except SlackApiError as e:
        print(f"슬랙 전송 오류: {e.response['error']}")

if __name__ == "__main__":
    content = get_web_data()
    send_slack_message(content)
