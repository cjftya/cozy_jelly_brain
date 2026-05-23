import requests
import json
import os

class JellySearch:
    def __init__(self):
        self.serper_api_key = None
        self.url = "https://google.serper.dev/search"

    def set_serper_api_key(self, api_key):
        self.serper_api_key = api_key

    def search(self, query):
        """
        Serper를 통해 Google 검색을 수행하고 상위 3개 결과를 정제
        """
        payload = json.dumps({
            "q": query,
            "num": 3  # 라이트웨이트 유지를 위해 3개로 제한
        })
        headers = {
            'X-API-KEY': self.serper_api_key,
            'Content-Type': 'application/json'
        }

        try:
            response = requests.request("POST", self.url, headers=headers, data=payload)
            data = response.json()
            
            # 검색 결과 중 'organic' 섹션에서 정보 추출
            results = data.get('organic', [])
            condensed = []
            for res in results:
                title = res.get('title', '제목 없음')
                snippet = res.get('snippet', '내용 없음')
                link = res.get('link', '')
                condensed.append(f"🔍 {title}\n   - 내용: {snippet}\n   - 출처: {link}")
            
            return "\n".join(condensed) if condensed else "검색 결과가 없습니다."
        except Exception as e:
            return f"외부 신호 수신 실패: {e}"