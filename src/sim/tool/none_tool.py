from sim.tool.base_tool import BaseTool
from sim.tool.tool_type import ToolType


class NoneTool(BaseTool):
    def __init__(self):
        super().__init__("none", ToolType.NONE)

    def get_description(self):
        return "파라미터 없음. 아무 행동도 하지 않고 대기."

    def get_params(self):
        return ""

    def execute(self, params, agent, world_system_manager):
        world_system_manager.log_world_event(f"{agent.name}가 행동을 하지 않음.")
