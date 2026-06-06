from sim.tool.base_tool import BaseTool
from sim.tool.tool_type import ToolType

class RestTool(BaseTool):
    def __init__(self):
        super().__init__("rest", ToolType.REST)

    def get_description(self):
        return "파라미터 없음. 안전하게 휴식을 취하여 피로도를 대폭 감소시키고 복잡한 인지 메모리를 정리함."

    def get_params(self):
        return ''

    def execute(self, params, agent, world_system_manager):
        agent.perform_brain_cleanup()
        agent.vital_state.update_fatigue(-90)
        agent.vital_state.update_health(30)
        world_system_manager.log_world_event(f"{agent.name}가 휴식함.")
        