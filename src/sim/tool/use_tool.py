from sim.tool.base_tool import BaseTool
from sim.object_meta.object_type import ObjectDetailType
from sim.tool.tool_type import ToolType

class UseTool(BaseTool):
    def __init__(self):
        super().__init__("use", ToolType.USE)

    def get_description(self):
        return "음식물을 먹어서 허기를 보충하거나, 거울을 보고 노트북을 조작하는 등 사물의 고유 기능과 서사적 상호작용을 '직접 실행'."

    def get_params(self):
        return '{"object_id": "Available Objects 중 하나 또는 My Inventory Objects 중 하나"}'

    def execute(self, params, agent, world_system_manager):
        object_id = params.get('object_id')
        is_my_inventory = False
        target_object = world_system_manager.object_manager.get_object_by_id(object_id)
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
                    world_system_manager.object_manager.pop_object_by_id(target_object.id)

                world_system_manager.log_world_event(f"{agent.name}가 {target_object.name}을 사용.")
            else:
                # 상태 변화가 일어나는 경우
                state, state_detail = target_object.get_current_state()
                if state and state_detail:
                    state_str = f" ({state} 상태로 전환)" if state else ""
                    world_system_manager.log_world_event(f"{agent.name}가 {target_object.name}을 사용함. {state_str}")
        else:
            world_system_manager.log_world_event(f"{agent.name}가 {object_id}을 사용할 수 없음.")