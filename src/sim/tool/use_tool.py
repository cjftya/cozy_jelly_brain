from sim.tool.base_tool import BaseTool
from sim.tool.tool_type import ToolType
from sim.action.use_action import UseAction

class UseTool(BaseTool):
    def __init__(self):
        super().__init__("use", ToolType.USE)

    def get_description(self):
        return "음식물을 먹어서 허기를 보충하거나, 거울을 보고 노트북을 조작하는 등 사물의 고유 기능과 서사적 상호작용을 '직접 실행'."

    def get_params(self):
        return '{"object_id": "Available Objects 중 하나 또는 My Inventory Objects 중 하나"}'

    def execute(self, params, agent, world_system_manager):
        object_id = params.get('object_id')
        if not object_id:
            world_system_manager.log_system_event("skip function call: use_tool, object_id not found")
            return

        use_action = UseAction(world_system_manager=world_system_manager)
        use_action.execute(agent.name, object_id)

    def _find_object_by_id(self, object_id, agent):
        target_object = self.world_system_manager.object_manager.get_object_by_id(object_id)
        if not target_object:
            target_object = agent.inventory.get_object_by_id(object_id)
        return target_object