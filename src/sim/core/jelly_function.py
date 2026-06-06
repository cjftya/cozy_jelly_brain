from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sim.world.world_system_manager import WorldSystemManager
from sim.tool.dynamic_tool_meta.dynamic_tool_executor import DynamicToolExecutor

class JellyFunction:
    def __init__(self, world_system_manager: "WorldSystemManager"):
        self.world_system_manager = world_system_manager

    def process_action_call(self, action_call, agent: "Agent"):
        function_name = action_call.get('function')
        
        has_tool = self.world_system_manager.tool_manager.has_tool_by_name(function_name)
        dynamic_tool_obj = None
        
        if not has_tool:
            # Fallback to search in agent's dynamic tools
            if agent and agent.dynamic_tool_manager:
                for dt in agent.dynamic_tool_manager.dynamic_tools:
                    if dt.name == function_name:
                        dynamic_tool_obj = dt
                        has_tool = True
                        break
                        
        if not has_tool:
            self.world_system_manager.log_system_event(f"Action Execution Error: {function_name}, error: function not found")
            return
        
        parameters = action_call.get('parameters', {})
        parameters['reason'] = action_call.get('reason', '이유 없음')
        agent.before_action = function_name
        agent.before_action_reason = parameters['reason']
        
        try:
            if dynamic_tool_obj:
                # Execute dynamic tool
                target_agent_name = parameters.get("target_agent_name") or parameters.get("applied_target")
                exec_params = {"applied_target": target_agent_name} if target_agent_name else {}
                DynamicToolExecutor.execute(dynamic_tool_obj, exec_params, agent, self.world_system_manager)
            else:
                # Execute standard static tool
                tool = self.world_system_manager.tool_manager.get_tool_by_name(function_name)
                tool.execute(parameters, agent, self.world_system_manager)
        except Exception as e:
            self.world_system_manager.log_system_event(f"Action Execution Error: {function_name}, error: {e}")