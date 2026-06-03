from sim.tool.base_tool import BaseTool
from sim.tool.dynamic_tool_meta.dynamic_tool_executor import DynamicToolExecutor
import json

class DynamicTool(BaseTool):
    def __init__(self, tool_data):
        super().__init__(tool_data.get("invented_tool"), "DYNAMIC_TOOL")
        self.creator = tool_data.get("creator")
        self.creator_id = tool_data.get("creator_id")
        self.skill_type = tool_data.get("skill_type")
        self.is_public = tool_data.get("is_public", False)
        self.description = tool_data.get("description", "")
        self.parameters = tool_data.get("parameters", {})
        self.effects = tool_data.get("effects", [])

    def get_description(self):
        return self.description

    def get_params(self):
        return json.dumps(self.parameters, ensure_ascii=False)

    def execute(self, params, agent, world_system_manager):
        DynamicToolExecutor.execute(self, params, agent, world_system_manager)