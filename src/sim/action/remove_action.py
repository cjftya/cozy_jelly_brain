from sim.action.base_action import BaseAction
from sim.object_meta.object_type import ObjectType

class RemoveAction(BaseAction):
    def __init__(self, world_system_manager):
        super().__init__(world_system_manager)

    def execute(self, *args):
        # args: target_id

        target_id = args[0]

        target_object = self.world_system_manager.object_manager.get_object_by_id(target_id)
        if not target_object:
            self.world_system_manager.log_system_event("skip function call: remove_action, object null")
            return
        
        if target_object.type == ObjectType.ITEM:
            self.world_system_manager.object_manager.pop_object_by_id(target_id)
            self._remove_from_all_agents(target_id)
            self.world_system_manager.log_world_event(f"{target_object.name}가 제거됨.")
        else:
            self.world_system_manager.log_system_event("skip function call: remove_action, object is not item")
            return

    def _remove_from_all_agents(self, target_id):
        for agent in self.world_system_manager.agent_manager.get_agents():
            agent.get_inventory().pop_object_by_id(target_id)

        