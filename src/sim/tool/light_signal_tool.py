from sim.tool.base_tool import BaseTool
from sim.tool.tool_type import ToolType

class LightSignalTool(BaseTool):
    def __init__(self):
        super().__init__("light_signal", ToolType.LIGHT_SIGNAL)

    def get_description(self):
        return "인벤토리에 '마른 나뭇가지'와 '부싯돌'이 수집되어 있을 때만 해안가에서 실행 가능함. 하늘 높이 거대한 연기 봉화를 피워 외부 구조를 요청함."

    def get_params(self):
        return ''

    def execute(self, params, agent, world_system_manager):
        inv = agent.get_inventory()
        branches = inv.find_item("마른 나뭇가지")
        flint = inv.find_item("부싯돌")
        
        if branches and flint:
            world_system_manager.log_world_event(f"{agent.name}가 해안가 암석 위에 자원들을 쌓고 부싯돌을 튕겨 거대한 연기 봉화를 피워 올림. 섬 안개를 뚫고 피어오른 검은 연기를 포착한 원양 수송선에 의해 기적적으로 구조됨")
            world_system_manager.log_system_event("CRITICAL_END: SIMULATION_SUCCESS_SIGNAL_ESCAPE")
            world_system_manager.event_trigger.stop()
        else:
            world_system_manager.log_world_event(f"{agent.name}가 구조 봉화를 피우려 했으나 필요한 자원(마른 나뭇가지 혹은 부싯돌)이 부족함")