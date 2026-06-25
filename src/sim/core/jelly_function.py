from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sim.world.world_system_manager import WorldSystemManager


class JellyFunction:
    def __init__(self, world_system_manager: "WorldSystemManager"):
        self.world_system_manager = world_system_manager

    def process_action_call(self, action_call, agent: "Agent"):
        function_name = action_call.get("function")

        has_tool = agent.tool_manager.has_tool_by_name(function_name)
        if not has_tool:
            self.world_system_manager.log_system_event(
                f"Action Execution Error: {function_name}, error: function not found"
            )
            return

        parameters = action_call.get("parameters", {})
        parameters["reason"] = action_call.get("reason", "이유 없음")

        try:
            tool = agent.tool_manager.get_tool_by_name(function_name)
            tool.execute(parameters, agent, self.world_system_manager)
        except Exception as e:
            self.world_system_manager.log_system_event(
                f"Action Execution Error: {function_name}, error: {e}"
            )
