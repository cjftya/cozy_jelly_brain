from sim.action.base_action import BaseAction
from sim.action.remove_action import RemoveAction
from sim.object_meta.object_type import ObjectDetailType

class UseAction(BaseAction):
    def __init__(self, world_system_manager):
        super().__init__(world_system_manager)

    def execute(self, *args):
        # args: agent_name, object_id
        if len(args) != 2:
            self.world_system_manager.log_system_event("skip function call: use, args length not 2")
            return

        agent_name = args[0]
        object_id = args[1]
        agent = self.world_system_manager.agent_manager.get_agent_by_name(agent_name)
        if not agent:
            self.world_system_manager.log_system_event("skip function call: use, agent null")
            return

        target_object = self.world_system_manager.object_manager.get_object_by_id(object_id)
        if not target_object:
            target_object = agent.get_inventory().get_object_by_id(object_id)

        if target_object:
            object_detail_type = target_object.detail_type
            if object_detail_type == ObjectDetailType.FOOD or object_detail_type == ObjectDetailType.DRINK:
                agent.vital_state.update_hunger(-target_object.nutrition_value)
            else:
                # 음식 이외 다른 것들 (감기약 등)
                pass

            # 소모품 제거 (모든 곳에서 제거)
            remove_action = RemoveAction(self.world_system_manager)
            remove_action.execute(object_id)

            self.world_system_manager.log_world_event(f"{agent.name}가 {target_object.name}을 사용.")
        else:
            self.world_system_manager.log_world_event(f"{agent.name}가 {object_id}을 사용할 수 없음.")