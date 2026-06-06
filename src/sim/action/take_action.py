from sim.action.base_action import BaseAction

class TakeAction(BaseAction):
    def __init__(self, world_system_manager):
        super().__init__(world_system_manager)

    def execute(self, *args):
        # args: agent_name, object_id
        if len(args) != 2:
            self.world_system_manager.log_system_event("skip function call: take, args length not 2")
            return

        agent_name = args[0]
        object_id = args[1]
        agent = self.world_system_manager.agent_manager.get_agent_by_name(agent_name)
        if not agent:
            self.world_system_manager.log_system_event("skip function call: take, agent null")
            return
            
        target_object = self.world_system_manager.object_manager.pop_object_by_id(object_id)
        if not target_object:
            self.world_system_manager.log_system_event("skip function call: take, target object null")
            return

        target_object.parent = agent
        agent.inventory.add_object(target_object)
        self.world_system_manager.log_world_event(f"{agent.name}가 {target_object.name}을 획득.")