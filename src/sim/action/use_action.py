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
            return False

        agent_name = args[0]
        object_id = args[1]
        agent = self.world_system_manager.agent_manager.get_agent_by_name(agent_name)
        if not agent:
            self.world_system_manager.log_system_event("skip function call: use, agent null")
            return False

        target_object = self.world_system_manager.object_manager.get_object_by_id(object_id)
        if not target_object:
            target_object = agent.inventory.get_object_by_id(object_id)

        if target_object:
            object_detail_type = target_object.detail_type
            if object_detail_type == ObjectDetailType.FOOD:
                agent.vital_state.update_hunger(target_object.hunger_recovery_value)
                agent.vital_state.update_fatigue(target_object.fatigue_recovery_value)
                agent.vital_state.update_health(target_object.health_recovery_value)
                agent.vital_state.update_mana(target_object.mana_recovery_value)

                remove_action = RemoveAction(self.world_system_manager)
                remove_action.execute(object_id)
                self.world_system_manager.log_world_event(f"{agent.name}가 {target_object.name}을 먹음.")
                return False # 바로 사용되기 때문에 피드백 없도록 처리
            else:
                # 소모되지 않는 도구들
                self.world_system_manager.log_world_event(f"{agent.name}가 {target_object.name}을 사용.")
                return True, target_object.use()
        else:
            self.world_system_manager.log_world_event(f"{agent.name}가 {object_id}을 사용할 수 없음.")
            return False