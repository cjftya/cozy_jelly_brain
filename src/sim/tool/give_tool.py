from sim.tool.base_tool import BaseTool
from sim.world.event_trigger import ThinkEventType
from sim.tool.tool_type import ToolType

class GiveTool(BaseTool):
    def __init__(self):
        super().__init__("give", ToolType.GIVE)

    def get_description(self):
        return "내가 소지한 물건을 다른 에이전트에게 양도."

    def get_params(self):
        return '{"agent_name": "Available Participants 중 한명", "object_id": "My Inventory Objects 중 하나"}'

    def execute(self, params, agent, world_system_manager):
        target_agent_name = params.get('agent_name')
        target_agent = world_system_manager.agent_manager.get_agent_by_name(target_agent_name)
        if not target_agent:
            world_system_manager.log_system_event("skip function call: give, target agent null")
            return
        
        object_id = params.get('object_id')
        target_object = agent.get_inventory().pop_object_by_id(object_id)
        if not target_object:
            world_system_manager.log_system_event("skip function call: give, target object null or not found in inventory")
            return

        target_agent.get_inventory().add_object(target_object)

        context = f"{agent.name}가 나에게 {target_object.name}를 주었음."
        target_agent.push_think_event(ThinkEventType.SPEAK, context, agent.name)
        world_system_manager.log_world_event(f"{agent.name}가 {target_agent.name}에게 {target_object.name}를 전달.")
        