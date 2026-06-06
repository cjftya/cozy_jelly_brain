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
            self._save_tools()
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
                "skill_type": tool.skill_type,
                "creator": tool.creator,
                "creator_id": tool.creator_id,
                "is_public": tool.is_public,
                "description": tool.description,
                "parameters": tool.parameters,
                "effects": tool.effects
            })
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def register_new_tool(self, tool_data):
        # 중복 검사 프로토콜 (동일 에이전트가 만든 동일 이름의 스킬만 중복 컬링)
        if any(t.name == tool_data["invented_tool"] and t.creator_id == tool_data.get("creator_id") for t in self.dynamic_tools):
            return False
            
        new_tool = DynamicTool(tool_data)
        self.dynamic_tools.append(new_tool)
        
        # 합산 최대 10개 한도 가드 및 FIFO 업데이트 규칙 적용
        if len(self.dynamic_tools) > 10:
            popped = self.dynamic_tools.pop(0)
            Logger.log_debug(f"[FIFO 스킬 풀] 저장 한도 초과로 오래된 스킬 밀려남: {popped.name}")
            
        self._save_tools()
        return True

    def get_tools_manual(self, agent, max_slots=5):
        prefix = "  "
        my_tools = [t for t in self.dynamic_tools if t.creator_id == agent.id]
        if not my_tools:
            return prefix + "- 사용 가능한 맞춤형 동적 스킬 없음"

        scored_tools = []
        vital = agent.vital_state
        is_vital_crisis = vital.hunger >= 80.0 or vital.fatigue >= 80.0 or vital.health <= 30.0

        for tool in my_tools:
            score = 10.0
            # 생체 위기 시 VITAL 관리용 스킬 슬롯 점수 폭발
            if tool.effects and is_vital_crisis:
                for effect in tool.effects:
                    if effect.get("meta_tag") == "VITAL_MODIFIER" and float(effect.get("intensity", 0)) > 0:
                        score += 50.0
            scored_tools.append((score, tool))

        # 점수 정렬 후 상황기반 5개만 LLM에 최종 노출
        scored_tools.sort(key=lambda x: x[0], reverse=True)
        top_tools = [t[1] for t in scored_tools][:max_slots]

        tools_context = []
        for tool in top_tools:
            tools_context.append(prefix + tool.get_manual())
        return "\n".join(tools_context)