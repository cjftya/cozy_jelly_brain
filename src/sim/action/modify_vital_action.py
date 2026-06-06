from sim.action.base_action import BaseAction
from sim.agent_meta.vital_state import VitalType

class ModifyVitalAction(BaseAction):
    def __init__(self, world_system_manager):
        super().__init__(world_system_manager)

    def execute(self, *args):
        # args: agent_name, vital_type, amount

        if len(args) != 3:
            self.world_system_manager.log_system_event("skip function call: modify_vital, args length not 3")
            return

        try:
            agent_name = args[0]
            vital_type = int(args[1])
            amount = float(args[2])

            target_agent = self.world_system_manager.agent_manager.get_agent_by_name(agent_name)
            if not target_agent:
                self.world_system_manager.log_system_event("skip function call: modify_vital, target agent null")
                return

            if vital_type == VitalType.HEALTH:
                target_agent.vital_state.update_health(amount)
            elif vital_type == VitalType.HUNGER:
                target_agent.vital_state.update_hunger(amount)
            elif vital_type == VitalType.FATIGUE:
                target_agent.vital_state.update_fatigue(amount)
            else:
                self.world_system_manager.log_system_event("skip function call: modify_vital, vital_type not found")
                return
            
            self.world_system_manager.log_world_event(f"{target_agent.name}의 {VitalType.to_string(vital_type)}가 {amount}만큼 변동되었습니다.")
        except Exception as e:
            self.world_system_manager.log_system_event(f"skip function call: modify_vital, error: {e}")