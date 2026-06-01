from sim.tool.base_tool import BaseTool
from sim.tool.tool_type import ToolType
from sim.world.event_trigger import ThinkEventType
from sim.action.remove_action import RemoveAction
from sim.action.create_action import CreateAction
from sim.object_meta.object_type import ObjectType
from sim.util.object_manager import ObjectManager

class CraftTool(BaseTool):
    def __init__(self):
        super().__init__("craft", ToolType.CRAFT)

    def get_description(self):
        return "가방이나 주변에 있는 재료(materials)를 조합하여 새로운 사물이나 구조물(target_creation)을 창조합니다."

    def get_params(self):
        return '''{
    "target_creation": "만들고자 하는 결과물의 이름 (예: 모닥불, 돌도끼, 뗏목 등)",
    "materials": [{"object_id": "재료의 고유 ID", "count": 1}]
}'''

    def execute(self, params, agent, world_system_manager):
        target_creation = params.get("target_creation", "알 수 없는 물건")
        materials = params.get("materials", [])
        
        world_system_manager.log_world_event(f"[World Mediator] '{target_creation}' 조합 심사 중...")

        # 현재 주변 객체 및 인벤토리 정보 취합
        current_location = agent.get_location_delegate().get_current_location()
        inv_context = agent.inventory.get_objects_full_context()
        
        # 공간 내 아이템 추출
        objects_of_location = world_system_manager.object_manager.get_objects_by_parent_name(current_location)
        env_objects = [obj for obj in objects_of_location if obj.type == ObjectType.ITEM]
        env_obj_manager = ObjectManager()
        env_obj_manager.add_objects(env_objects)
        env_context = env_obj_manager.get_objects_full_context()

        # 미디에이터에게 O/X 심사 요청
        response = world_system_manager.world_mediator.request_craft_approval(agent.name, target_creation, materials)

        if not response or not response.get("approved"):
            reason = response.get("reason", "물리적으로 불가능한 조합임.")
            agent.push_think_event(ThinkEventType.PLANNING, f"'{target_creation}' 제작에 실패함: {reason}")
            world_system_manager.log_world_event(f"{agent.name}의 '{target_creation}' 제작 시도가 실패로 돌아감.")
            return

        # 승인 시: 재료 차감 (RemoveAction)
        consumed_objects = response.get("consumed_objects", [])
        remove_action = RemoveAction(world_system_manager)
        for consumed in consumed_objects:
            obj_id = consumed.get("object_id")
            count = int(consumed.get("consumed_count", 1))
            for _ in range(count):
                remove_action.execute(obj_id)

        created_object_type = response.get("created_object_type", ObjectType.ITEM)
        
        create_action = CreateAction(world_system_manager)
        create_action.execute(target_creation, current_location, agent.position.x, agent.position.y, created_object_type)

        # 성공 피드백
        success_msg = f"'{target_creation}'을(를) 물리적으로 완성함."
        agent.push_think_event(ThinkEventType.PLANNING, success_msg)
        world_system_manager.log_world_event(f"{agent.name}가 재료를 소모해 '{target_creation}'을 완성함")