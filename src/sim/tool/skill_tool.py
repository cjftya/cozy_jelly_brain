import random
from sim.tool.base_tool import BaseTool
from sim.tool.tool_type import ToolType
from sim.world.event_trigger import ThinkEventType
from sim.core.jelly_llm_api import JellyLlmApi
from sim.object_meta.object_type import ObjectType
from sim.util.object_manager import ObjectManager
from sim.action.remove_action import RemoveAction
from sim.action.create_action import CreateAction
from sim.tool.dynamic_tool_meta.dynamic_tool_executor import DynamicToolExecutor
from sim.tool.dynamic_tool import DynamicTool

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
    "invented_tool": "발현하고자 하는 능력 또는 물질의 명사형 이름 또는 상태 (예: 파이어볼, 상한 음식, 독 정화, 박스 정리)",
    "target_agent_name": "Available Participants 중 한명 (skill_type이 'agent_skill'일 경우에만 필수 이외는 null로 표기)",
    "target_object_id": "Available Objects 중 하나 또는 My Inventory Objects 중 하나 (skill_type이 'object_transform'일 경우에만 필수 이외는 null로 표기)"
}'''

    def execute(self, params, agent, world_system_manager):
        skill_type = params.get("skill_type", "unknown_skill_type")
        invented_tool = params.get("invented_tool", "unknown_action")
        target_agent_name = params.get("target_agent_name", "null")
        target_object_id = params.get("target_object_id", "null")
        execute_reason = params.get("reason", "unknown_reason")

        world_system_manager.log_world_event(f"{agent.name}가 Skill '{invented_tool}' 행동을 시도 함.")

        if skill_type == "object_craft":
            self._execute_object_craft(invented_tool, agent, execute_reason, world_system_manager)
        elif skill_type == "object_transform":
            self._execute_object_transform(invented_tool, target_object_id, agent, execute_reason, world_system_manager)
        elif skill_type == "agent_skill":
            self._execute_agent_skill(invented_tool, target_agent_name, agent, execute_reason, world_system_manager)
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
            
            # 대표 name를 통해 사물의 고유 이름(예: '단단한 야자나무 통나무')을 알아냄
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
        create_action.execute(name, agent.name, description)

        # 성공 피드백
        success_msg = f"'{name}'를 생성함."
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

        agent.dynamic_tool_manager.register_new_tool({
            "invented_tool": invented_tool,
            "skill_type": "object_transform",
            "creator": agent.name,
            "creator_id": agent.id,
            "is_public": True,
            "description": f"대상 [{target_object.name}]을(를) {state_name} 상태로 영구 변형.",
            "parameters": {"target_object_id": target_object_id},
            "effects": []
        })

        # 성공 피드백
        success_msg = f"'{target_object.name}'의 상태를 '{state_name}'(으)로 변형함."
        agent.push_think_event(ThinkEventType.PLANNING, success_msg)
        world_system_manager.log_world_event(f"{agent.name}가 '{target_object.name}'의 상태를 '{state_name}'(으)로 변형함")

    def _execute_agent_skill(self, invented_tool, target_agent_name, agent, execute_reason, world_system_manager):
        if target_agent_name == "null" or target_agent_name == agent.name:
            target_agent_name = agent.name

        mediator_response = world_system_manager.world_mediator.request_agent_skill(
            agent.name, invented_tool, execute_reason, target_agent_name
        )
        print(mediator_response)

        if not mediator_response or mediator_response.get("rejected", False):
            reason = mediator_response.get("reject_reason", "우주의 인과율이 이 능력의 도약을 기각함.")
            agent.push_think_event(ThinkEventType.PLANNING, f"'{invented_tool}' 능력 발현에 실패함: {reason}")
            world_system_manager.log_world_event(f"{agent.name}의 스킬 생성 요청이 거부됨.")
            return

        effects = mediator_response.get("effects", [])
        description = mediator_response.get("description", "정제된 스킬 설명")

        # 스킬 풀 시스템 캐싱 연동 등록
        tool_data = {
            "invented_tool": invented_tool,
            "skill_type": "agent_skill",
            "creator": agent.name,
            "creator_id": agent.id,
            "is_public": True,
            "description": description,
            "parameters": {"target_agent_name": target_agent_name},
            "effects": effects
        }
        agent.dynamic_tool_manager.register_new_tool(tool_data)

        DynamicToolExecutor.execute(DynamicTool(tool_data), {"applied_target": target_agent_name}, agent, world_system_manager)

        success_msg = f"새로운 스킬 [{invented_tool}] 발현 및 등록 완료."
        agent.push_think_event(ThinkEventType.PLANNING, success_msg)

    def _find_objects_by_name(self, object_name, agent, world_system_manager):
        target_object = world_system_manager.object_manager.get_pack(object_name)
        if target_object:
            return target_object
        
        target_object = agent.inventory.get_pack(object_name)
        if target_object:
            return target_object
        
        return None

    def _find_object_by_id(self, object_id, agent, world_system_manager):
        target_object = world_system_manager.object_manager.get_object_by_id(object_id)
        if target_object:
            return target_object
        
        target_object = agent.inventory.get_object_by_id(object_id)
        if target_object:
            return target_object
        
        return None

