from sim.tool.base_tool import BaseTool
from sim.world.event_trigger import ThinkEventType
from sim.tool.tool_type import ToolType

class RuleMakeTool(BaseTool):
    def __init__(self):
        super().__init__("rule_make", ToolType.RULE_MAKE)

    def get_description(self):
        return "정말 절박하고 탈출할 수 없는 최악의 절망적 상황에서 생존을 위한 규칙을 만드는 도구. 새로운 규칙을 생성하면 너의 행동 기준이 영구적으로 변경된다."

    def get_params(self):
        return '{"rule": "새로운 규칙 내용"}'

    def execute(self, params, agent, world_system_manager):
        pass