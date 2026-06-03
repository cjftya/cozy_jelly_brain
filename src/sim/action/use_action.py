from sim.action.base_action import BaseAction
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

        is_my_inventory = False
        target_object = self.world_system_manager.object_manager.get_object_by_id(object_id)
        if not target_object:
            is_my_inventory = True
            target_object = agent.get_inventory().get_object_by_id(object_id)

        if target_object:
            object_detail_type, is_consumed = target_object.use()
            if is_consumed:
                # 소모품 사용
                if object_detail_type == ObjectDetailType.FOOD or object_detail_type == ObjectDetailType.DRINK:
                    agent.vital_state.update_hunger(-target_object.nutrition_value)
                else:
                    # 음식 이외 다른 것들 (감기약 등)
                    pass

                # 소모품 제거 (모든 곳에서 제거)
                if is_my_inventory:
                    agent.get_inventory().pop_object_by_id(target_object.id)
                else:
                    self.world_system_manager.object_manager.pop_object_by_id(target_object.id)

                self.world_system_manager.log_world_event(f"{agent.name}가 {target_object.name}을 사용.")
            else:
                # 상태 변화가 일어나는 경우
                state, state_detail = target_object.get_current_state()
                if state and state_detail:
                    state_str = f" ({state} 상태로 전환)" if state else ""
                    self.world_system_manager.log_world_event(f"{agent.name}가 {target_object.name}을 사용함. {state_str}")
        else:
            self.world_system_manager.log_world_event(f"{agent.name}가 {object_id}을 사용할 수 없음.")