from sim.tool.base_tool import BaseTool
from sim.world.event_trigger import ThinkEventType
from sim.tool.tool_type import ToolType

class InspectTool(BaseTool):
    def __init__(self):
        super().__init__("inspect", ToolType.INSPECT)

    def get_description(self):
        return "인간 지각 범위 내에 있는 특정 오브젝트의 숨겨진 서사적 상세 정보와 상세 정보(detail)를 면밀히 관찰하고 식별함."

    def get_params(self):
        return '{"object_id": "Available Objects 중 하나"}'

    def execute(self, params, agent, world_system_manager):
        reason = params.get('reason', None)
        object_id = params.get('object_id')
        target_object = world_system_manager.object_manager.get_object_by_id(object_id)
        if not target_object:
            world_system_manager.log_system_event("skip function call: inspect, target object null " + object_id)
            return

        target_object.is_inspected = True
        context = f"나는 {target_object.name}에 대한 상세 정보를 얻었다. 더이상 관찰할 필요가 없다. 이제 이 관찰을 바탕으로 다음 계획을 세우자. (관찰한 결과: {target_object.detail})"
        agent.push_think_event(ThinkEventType.INSPECT, context, agent.name)
        world_system_manager.log_world_event(f"{agent.name}가 {target_object.name}을 상세히 관찰.")
        