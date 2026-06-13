from sim.tool.base_tool import BaseTool
from sim.tool.tool_type import ToolType
from sim.action.take_action import TakeAction
from sim.world.event_trigger import ThinkEventType

class TakeTool(BaseTool):
    def __init__(self):
        super().__init__("take", ToolType.TAKE)

    def get_description(self):
        return "바닥이나 구역에 놓인 물체를 내 소유(인벤토리)로 획득."

    def get_params(self):
        return '{"object_id": "Available Objects 중 하나"}'

    def execute(self, params, agent, world_system_manager):
        object_id = params.get('object_id')
        if not object_id:
            world_system_manager.log_system_event("skip function call: take_tool, object_id not found")
            return

        action = TakeAction(world_system_manager)
        if action.execute(agent.name, object_id):
            target_object = agent.inventory.get_object_by_id(object_id)
            if target_object:
                agent.push_think_event(ThinkEventType.PLANNING, f"{target_object.name}을 획득했음.")