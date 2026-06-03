import random
from sim.tool.base_tool import BaseTool
from sim.tool.tool_type import ToolType
from sim.world.event_trigger import ThinkEventType
from sim.core.jelly_llm_api import JellyLlmApi
from sim.object_meta.object_type import ObjectType
from sim.util.object_manager import ObjectManager

class SkillTool(BaseTool):
    def __init__(self):
        super().__init__("skill", ToolType.SKILL)

    def get_description(self):
        return (
            "[핵심 창조 및 권능 발현 도구] 기본 도구(이동, 대화 등)만으로 해결할 수 없는 상황에서, "
            "세계에 새로운 물질을 창조하거나, 사물을 변형하거나, 자신/타인에게 영향을 주는 고유 능력을 발현합니다. "
            "당신의 의도는 세계의 절대 법칙(Mediator)의 심사를 거쳐 통과될 경우 월드에 영구 적용되거나 스킬 풀에 등록됩니다."
        )

    def get_params(self):
        return '''{
    "skill_type": "원하는 능력의 타입 선택 (object_craft: 물질의 창조 / object_transform: 사물의 상태 변형 / agent_skill: 에이전트 대상 능력 발현)",
    "invented_tool": "발현하고자 하는 능력 또는 물질의 명사형 이름 (예: 파이어볼, 상한 음식, 독 정화, 박스 정리)"
}'''

    def execute(self, params, agent, world_system_manager):
        skill_type = params.get("skill_type", "unknown_skill_type")
        invented_tool = params.get("invented_tool", "unknown_action")

        world_system_manager.log_world_event(f"{agent.name}가 Skill '{invented_tool}' 행동을 시도 함.")

        if skill_type == "object_craft":
            self._execute_object_craft(invented_tool, agent, world_system_manager)
        elif skill_type == "object_transform":
            self._execute_object_transform(invented_tool, agent, world_system_manager)
        elif skill_type == "agent_skill":
            self._execute_agent_skill(invented_tool, agent, world_system_manager)
        else:
            world_system_manager.log_world_event(f"{agent.name}가 '{invented_tool}'을(를) 사용하려고 시도 했으나 실패 함.")

    def _execute_object_craft(self, invented_tool, agent, world_system_manager):
        # 현재 주변 객체 및 인벤토리 정보 취합
        current_location = agent.get_location_delegate().get_current_location()
        inv_context = agent.inventory.get_objects_full_context()
        
        # 공간 내 아이템 추출
        objects_of_location = world_system_manager.object_manager.get_objects_by_parent_name(current_location)
        env_objects = [obj for obj in objects_of_location if obj.type == ObjectType.ITEM]
        env_obj_manager = ObjectManager()
        env_obj_manager.add_objects(env_objects)
        env_context = env_obj_manager.get_objects_full_context()

        materials_context = inv_context + "\n" + env_context

        response = world_system_manager.world_mediator.request_craft_approval(agent.name, target_creation, materials_context)

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

    def _execute_object_transform(self, params, agent, world_system_manager):
        pass

    def _execute_agent_skill(self, params, agent, world_system_manager):
        pass