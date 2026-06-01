from sim.tool.base_tool import BaseTool
from sim.tool.dynamic_tool_meta.dynamic_tool_executor import DynamicToolExecutor
import json

class DynamicTool(BaseTool):
    def __init__(self, tool_data):
        # tool_data는 dynamic_tools.json에서 읽어온 딕셔너리
        super().__init__(tool_data.get("invented_tool"), "DYNAMIC_TOOL")
        self.creator = tool_data.get("creator")
        self.is_public = tool_data.get("is_public", False)
        self.description = tool_data.get("description", "")
        self.parameters = tool_data.get("parameters", {})
        self.effects = tool_data.get("effects", [])

    def get_description(self):
        return self.description

    def get_params(self):
        # LLM 시스템 프롬프트에 들어갈 파라미터 매뉴얼 텍스트화
        return json.dumps(self.parameters, ensure_ascii=False)

    def execute(self, params, agent, world_system_manager):
        # 실제 실행 로직은 이후 작성할 DynamicToolExecutor로 위임하거나 여기서 직접 처리합니다.
        DynamicToolExecutor.execute(self, params, agent, world_system_manager)