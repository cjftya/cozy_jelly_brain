import json
import random

import requests

from sim.tool.base_tool import BaseTool
from sim.tool.tool_type import ToolType
from sim.world.event_trigger import ThinkEventType


class WebSearchTool(BaseTool):
    def __init__(self):
        super().__init__("web_search", ToolType.WEB_SEARCH)
        self.url = "https://google.serper.dev/search"

    def get_description(self):
        return "궁금한 내용을 외부 가상 네트워크(웹)에서 필요한 실시간 정보나 지식을 동적으로 검색하고 수집함."

    def get_params(self):
        return '{"query": "웹에서 검색할 핵심 키워드 또는 질의어."}'

    def execute(self, params, agent, world_system_manager):
        if isinstance(params, str):
            try:
                params = json.loads(params)
            except Exception:
                params = {"query": params}

        reason = params.get("reason", None)
        query = params.get("query", "") if isinstance(params, dict) else str(params)
        res = self.web_search(query, world_system_manager.serper_api_key)

        context = f"[{reason}] 라는 이유로, 나는 '{query}'에 대해 웹 검색을 함. 검색 결과:\n{res}"
        agent.push_think_event(ThinkEventType.WEB_SEARCH, context, agent.name)

        world_system_manager.log_world_event(f"{agent.name}가 웹 검색을 함.")

    def web_search(self, query, serper_api_key):
        if not serper_api_key:
            return "외부 신호 수신 실패: Serper API Key가 시스템 매니저에 등록되지 않았습니다."

        payload = json.dumps(
            {
                "q": query,
                "num": 3,  # 컨텍스트 블로팅(Bloating)을 막기 위한 v8 컴팩트 규격 적용
            }
        )
        headers = {"X-API-KEY": serper_api_key, "Content-Type": "application/json"}

        try:
            response = requests.request(
                "POST", self.url, headers=headers, data=payload, timeout=5
            )
            data = response.json()

            results = data.get("organic", [])
            condensed = []
            for res in results:
                title = res.get("title", "제목 없음")
                snippet = res.get("snippet", "내용 없음")
                link = res.get("link", "")
                condensed.append(f"[{title}]\n   - 정보: {snippet}\n   - 출처: {link}")

            return "\n\n".join(condensed) if condensed else "검색 결과가 존재하지 않음"
        except Exception as e:
            return f"외부 네트워크 연결 실패 및 신호 수신 오류: {e}"
