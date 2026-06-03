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
        prefix = "  "
        # TODO: 추가예정
        tools_context = []
        for tool in self.dynamic_tools:
            tools_context.append(prefix + tool.get_manual())
        return "\n".join(tools_context)
