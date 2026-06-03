from sim.tool.base_tool import BaseTool
from sim.world.event_trigger import ThinkEventType
from sim.tool.tool_type import ToolType
from sim.action.give_action import GiveAction

class GiveTool(BaseTool):
    def __init__(self):
        super().__init__("give", ToolType.GIVE)

    def get_description(self):
        return "내가 소지한 물건을 다른 에이전트에게 양도."

    def get_params(self):
        return '{"agent_name": "Available Participants 중 한명", "object_id": "My Inventory Objects 중 하나"}'

    def execute(self, params, agent, world_system_manager):
        target_agent_name = params.get('agent_name')
        target_object_id = params.get('object_id')
        if not target_agent_name or not target_object_id:
            world_system_manager.log_system_event("skip function call: give_tool, target_agent_name or target_object_id not found")
            return

        action = GiveAction(world_system_manager=world_system_manager)
        action.execute(target_agent_name, agent.name, target_object_id)