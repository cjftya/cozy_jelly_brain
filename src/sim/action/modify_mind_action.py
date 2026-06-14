from sim.action.base_action import BaseAction

class ModifyMindAction(BaseAction):
    def __init__(self, world_system_manager):
        super().__init__(world_system_manager)

    def execute(self, *args):
        # args: target_agent_name, key_name, score
        if len(args) != 3:
            self.world_system_manager.log_system_event("skip function call: modify_mind, args length not 3")
            return False

        target_agent_name = args[0]
        key_name = args[1]
        value_delta = float(args[2])

        target_agent = self.world_system_manager.agent_manager.get_agent_by_name(target_agent_name)
        if not target_agent:
            self.world_system_manager.log_system_event("skip function call: modify_mind, target agent null")
            return False

        try:
            matrix = target_agent.personality_delegate.get_matrix()
            
            # 키에 대한 값 가져오기 (기본값 0.5)
            current_value = matrix.get(key_name, 0.5)
            
            # 값 계산 (0.0 ~ 1.0 사이 값으로 제한)
            new_value = max(0.0, min(1.0, current_value + value_delta))
            
            # 적용
            matrix[key_name] = new_value
            
            self.world_system_manager.log_world_event(f"{target_agent_name}의 {key_name} -> {new_value}로 변경됨")
            return True

        except Exception as e:
            self.world_system_manager.log_system_event(f"skip function call: modify_mind, error: {e}")
            return False