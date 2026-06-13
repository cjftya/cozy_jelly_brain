import random
from sim.tool.base_tool import BaseTool
from sim.tool.tool_type import ToolType
from sim.world.event_trigger import ThinkEventType
from sim.core.jelly_llm_api import JellyLlmApi
from sim.object_meta.object_type import ObjectType
from sim.util.object_manager import ObjectManager
from sim.action.remove_action import RemoveAction
from sim.action.create_action import CreateAction

class SkillTool(BaseTool):
    def __init__(self):
        super().__init__("skill", ToolType.SKILL)

    def get_description(self):
        return "[창조/변형 권능] 기본 도구로 해결할 수 없는 상황에서 새로운 물질을 제작(object_craft)하거나 사물의 상태를 영구 변형(object_transform)함. 절대 법칙(Mediator)의 심사를 거쳐 월드에 반영되며 시전 시 정신력(Mana)이 소모됨."

    def get_params(self):
        return '''{
    "skill_type": "원하는 능력의 타입 선택 (object_craft: 물건을 만들거나 요리하기 / object_transform: 물건의 상태 바꾸기)",
    "invented_tool": "발현하고자 하는 능력 또는 물질의 명사형 이름 또는 상태 (예: 힐링 포션, 이동석, 정화, 물체 정리)",
    "target_object_id": "Available Objects 중 하나 또는 My Inventory Objects 중 하나 (skill_type이 'object_transform'일 경우에만 필수 이외는 null로 표기)"
}'''

    def execute(self, params, agent, world_system_manager):
        skill_type = params.get("skill_type", "unknown_skill_type")
        invented_tool = params.get("invented_tool", "unknown_action")
        target_object_id = params.get("target_object_id", "null")
        execute_reason = params.get("reason", "unknown_reason")

        world_system_manager.log_world_event(f"{agent.name}가 Skill '{invented_tool}' 행동을 시도 함.")

        if skill_type == "object_craft":
            self._execute_object_craft(invented_tool, agent, execute_reason, world_system_manager)
        elif skill_type == "object_transform":
            self._execute_object_transform(invented_tool, target_object_id, agent, execute_reason, world_system_manager)
        else:
            world_system_manager.log_world_event(f"{agent.name}가 '{invented_tool}'을(를) 사용하려고 시도 했으나 실패 함.")

    def _execute_object_craft(self, invented_tool, agent, execute_reason, world_system_manager):
        # 현재 주변 객체 및 인벤토리 정보 취합
        current_location = agent.location_delegate.get_current_location()
        inv_context = agent.inventory.get_objects_full_context()
        
        # 공간 내 아이템 추출
        objects_of_location = world_system_manager.object_manager.get_objects_by_parent_name(current_location)
        env_objects = [obj for obj in objects_of_location if obj.type == ObjectType.ITEM]
        env_obj_manager = ObjectManager()
        env_obj_manager.add_objects(env_objects)
        env_context = env_obj_manager.get_objects_full_context()

        materials_context = inv_context + "\n" + env_context

        mediator_response = world_system_manager.world_mediator.request_object_craft(agent.name, invented_tool, execute_reason, materials_context)
        print(mediator_response)

        mana_cost = mediator_response.get("mana_cost", 0)
        if agent.vital_state.mana < mana_cost:
            agent.push_think_event(ThinkEventType.PLANNING, f"{invented_tool} 사용 실패. 정신력 부족. 소모치: {mana_cost}, 현재: {agent.vital_state.mana}")
            world_system_manager.log_world_event(f"{agent.name}가 스킬 {invented_tool}을 사용하려고 시도 했으나 정신력 부족으로 실패 함.")
            return
        
        if not mediator_response or mediator_response.get("rejected", False):
            reason = mediator_response.get("reject_reason", "물리적으로 불가능한 조합임.")
            agent.push_think_event(ThinkEventType.PLANNING, f"'{invented_tool}' 제작에 실패함: {reason}")
            world_system_manager.log_world_event(f"{agent.name}의 '{invented_tool}' 제작 시도가 실패로 돌아감.")
            return

        approved_skill = mediator_response.get("approved_skill", {})

        # 승인 시: 재료 차감 (RemoveAction)
        consumed_objects = mediator_response.get("used_objects", [])
        remove_action = RemoveAction(world_system_manager)

        for consumed in consumed_objects:
            rep_name = consumed.get("object_name")
            count = int(consumed.get("consumed_count", 1))
            
            remove_count = 0
            rep_objs = self._find_objects_by_name(rep_name, agent, world_system_manager)
            for obj in list(rep_objs):
                if obj.parent.name == current_location or obj.parent.name == agent.name:
                    remove_action.execute(obj.id)
                    remove_count += 1
                    if remove_count >= count:
                        break

        # 생성
        name = approved_skill.get("name", invented_tool)
        description = approved_skill.get("description", "설명 없음")
        create_action = CreateAction(world_system_manager)
        if create_action.execute(name, agent.name, description):
            agent.vital_state.update_mana(-mana_cost)

            # 성공 피드백
            success_msg = f"'{name}'를 생성함. 소모된 정신력: {mana_cost}"
            agent.push_think_event(ThinkEventType.PLANNING, success_msg)
            world_system_manager.log_world_event(f"{agent.name}가 재료를 소모해 '{name}'을 완성함")

    def _execute_object_transform(self, invented_tool, target_object_id, agent, execute_reason, world_system_manager):
        target_object = self._find_object_by_id(target_object_id, agent, world_system_manager)
        if target_object is None:
            world_system_manager.log_world_event(f"{agent.name}가 '{invented_tool}'을(를) 사용하려고 시도 했으나 실패 함.")
            return

        mediator_response = world_system_manager.world_mediator.request_object_transform(agent.name, target_object.name, execute_reason)
        print(mediator_response)

        if not mediator_response or mediator_response.get("rejected", False):
            reason = mediator_response.get("reject_reason", "상태변화가 불가능함.")
            agent.push_think_event(ThinkEventType.PLANNING, f"'{invented_tool}' 변형에 실패함: {reason}")
            world_system_manager.log_world_event(f"{agent.name}의 '{invented_tool}' 변형 시도가 실패로 돌아감.")
            return

        approved_skill = mediator_response.get("approved_skill", {})
        state_name = approved_skill.get("state_name", "변형됨")
        description = approved_skill.get("description", "설명 없음")
        
        target_object.set_state(state_name, description)

        mana_cost = mediator_response.get("mana_cost", 0)
        if agent.vital_state.mana < mana_cost:
            agent.push_think_event(ThinkEventType.PLANNING, f"{invented_tool} 사용 실패. 정신력 부족. 소모치: {mana_cost}, 현재: {agent.vital_state.mana}")
            world_system_manager.log_world_event(f"{agent.name}가 스킬 {invented_tool}을 사용하려고 시도 했으나 정신력 부족으로 실패 함.")
            return

        agent.vital_state.update_mana(-mana_cost)

        # 성공 피드백
        success_msg = f"'{target_object.name}'의 상태를 '{state_name}'(으)로 변형함. 소모된 정신력: {mana_cost}"
        agent.push_think_event(ThinkEventType.PLANNING, success_msg)
        world_system_manager.log_world_event(f"{agent.name}가 '{target_object.name}'의 상태를 '{state_name}'(으)로 변형함")

    def _find_objects_by_name(self, object_name, agent, world_system_manager):
        target_object = world_system_manager.object_manager.get_objects_by_name(object_name)
        if target_object:
            return target_object
        
        target_object = agent.inventory.get_objects_by_name(object_name)
        if target_object:
            return target_object
        
        return []

    def _find_object_by_id(self, object_id, agent, world_system_manager):
        target_object = world_system_manager.object_manager.get_object_by_id(object_id)
        if target_object:
            return target_object
        
        target_object = agent.inventory.get_object_by_id(object_id)
        if target_object:
            return target_object
        
        return None

