from sim.action.base_action import BaseAction

class GiveAction(BaseAction):
    def __init__(self, world_system_manager):
        super().__init__(world_system_manager)

    def execute(self, *args):
        # args: target_agent_name, source_agent_name, object_id
        if len(args) != 3:
            self.world_system_manager.log_system_event("skip function call: give, args length not 3")
            return
        target_agent_name = args[0]
        source_agent_name = args[1]
        object_id = args[2]
        target_agent = self.world_system_manager.agent_manager.get_agent_by_name(target_agent_name)
        source_agent = self.world_system_manager.agent_manager.get_agent_by_name(source_agent_name)
        if not target_agent or not source_agent:
            self.world_system_manager.log_system_event("skip function call: give, target or source agent null")
            return
        
        target_object = source_agent.get_inventory().pop_object_by_id(object_id)
        if not target_object:
            self.world_system_manager.log_system_event("skip function call: give, target object null or not found in inventory")
            return

        target_agent.get_inventory().add_object(target_object)