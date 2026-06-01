import json
import os
from sim.tool.dynamic_tool import DynamicTool
from log import Logger

class DynamicToolManager:
    def __init__(self):
        self.dynamic_tools = []
        self.db_path = None

    def start(self, db_path):
        self.db_path = os.path.join(db_path, "dynamic_tools.json")
        self._load_tools()

    def _load_tools(self):
        if not os.path.exists(self.db_path):
            self._save_tools() # 빈 파일 생성
            return
            
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for t_data in data.get("tools", []):
                    self.dynamic_tools.append(DynamicTool(t_data))
        except Exception as e:
            Logger.log("Error", f"동적 도구 로드 실패: {e}")

    def _save_tools(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        data = {"tools": []}
        for tool in self.dynamic_tools:
            data["tools"].append({
                "invented_tool": tool.name,
                "creator": tool.creator,
                "is_public": tool.is_public,
                "description": tool.description,
                "parameters": tool.parameters,
                "effects": tool.effects
            })
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def register_new_tool(self, tool_data):
        """미디에이터의 승인을 받은 새로운 도구를 영구 등록합니다."""
        # 중복 이름 방지
        if any(t.name == tool_data["invented_tool"] for t in self.dynamic_tools):
            return False
            
        new_tool = DynamicTool(tool_data)
        self.dynamic_tools.append(new_tool)
        self._save_tools()
        return True

    def get_tools_manual(self, agent, max_slots=5):
        """
        현재 에이전트의 상태(결핍, 사회적 고립 등)를 분석하여
        가장 시급한 Top N개의 동적 도구 매뉴얼을 기존 툴과 동일한 규격으로 반환합니다.
        """
        if not self.dynamic_tools:
            return ""

        scored_tools = []
        
        # 1. 에이전트의 현재 위기 상태 파악
        is_vital_crisis = agent.vital_state.hunger >= 80.0 or agent.vital_state.fatigue >= 80.0 or agent.vital_state.health <= 20.0
        available_participants = agent.participants_delegate.get_available_participants()
        is_socially_isolated = isinstance(available_participants, str) or len(available_participants) == 0
        
        for tool in self.dynamic_tools:
            # 2. 소유권 필터링 (내 것이 아니면서 공용이 아니면 제외)
            if not tool.is_public and tool.creator != agent.name:
                continue
                
            score = 10.0 # 기본 가중치
            tags = [effect.get("meta_tag") for effect in tool.effects]

            # 3. 생존 위기 (Vital Crisis) 필터 - 터널 비전 모사
            if is_vital_crisis:
                if "VITAL_MODIFIER" in tags or "ITEM_CONSUME" in tags:
                    score += 50.0 # 생존 직결 툴은 무조건 1순위로 끌어올림
                else:
                    score -= 10.0 # 위기 상황에 불필요한 행동(예: 건축, 농담)은 후순위로 밀림

            # 4. 사회적 고립 (Social Isolation) 필터 - 할루시네이션 방어
            if is_socially_isolated:
                if "BOND_MODIFIER" in tags or "MIND_MODIFIER" in tags:
                    score = -999.0 # 주변에 아무도 없는데 타인 대상 툴을 쓰려는 시도 원천 차단
            
            scored_tools.append((score, tool))

        # 5. 우선순위 점수(score) 기반 내림차순 정렬
        scored_tools.sort(key=lambda x: x[0], reverse=True)
        
        # 6. 상위 max_slots 개수만큼 잘라내기 (-999점 받은 툴은 제외)
        top_tools = [t[1] for t in scored_tools if t[0] > 0][:max_slots]

        # 7. 기존 ToolManager와 100% 동일하게 .get_manual() 호출 후 조인
        tools_context = []
        for tool in top_tools:
            tools_context.append(tool.get_manual())
            
        return "\n".join(tools_context)
