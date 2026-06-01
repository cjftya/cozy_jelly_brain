import random
from sim.tool.base_tool import BaseTool
from sim.tool.tool_type import ToolType
from sim.world.event_trigger import ThinkEventType
from sim.core.jelly_llm_api import JellyLlmApi
from sim.object_meta.object_type import ObjectType
from sim.util.object_manager import ObjectManager

class CustomRuleTool(BaseTool):
    def __init__(self):
        super().__init__("custom_rule", ToolType.CUSTOM_RULE)

    def get_description(self):
        return (
            "[궁극의 생존 창조 도구] 현재 주어진 도구만으로는 당면한 위기를 타개할 수 없을 때, 생존 본능을 발휘하여 "
            "스스로 새로운 행동(invented_tool)을 구상합니다. 원하는 행동의 이름과 그 서사적 묘사(description)만 제출하면, "
            "세계관의 법칙에 따라 성공 여부와 효과가 결정됩니다."
        )

    def get_params(self):
        return '''{
    "invented_tool": "창조할 행동 이름 (예: build_trap, forage_berry)",
    "description": "어떤 의도로 어떤 행동을 할 것인지 20자 내외로 명확하게 묘사"
}'''

    def execute(self, params, agent, world_system_manager):
        invented_tool = params.get("invented_tool", "unknown_action")
        description = params.get("description", "알 수 없는 행동을 구상.")

        world_system_manager.log_world_event(f"[World Mediator] '{invented_tool}' 심사 진행 중...")

        inventory_objects_context = agent.inventory.get_objects_full_context()
        current_location = agent.get_location_delegate().get_current_location()
        objects_of_location = world_system_manager.object_manager.get_objects_by_parent_name(current_location)
        available_objects = []
        for obj in objects_of_location:
            if obj.type == ObjectType.ITEM:
                available_objects.append(obj)

        obj_manager = ObjectManager()
        obj_manager.add_objects(available_objects)
        available_objects_context = obj_manager.get_objects_full_context()
        
        mediator_response = world_system_manager.world_mediator.request_invented_tool(
            agent.name, invented_tool, description, current_location, available_objects_context, inventory_objects_context
        )

        print(mediator_response)
        
        # 기각 처리
        if not mediator_response or mediator_response.get("rejected"):
            reject_reason = mediator_response.get("reject_reason", "물리적으로 불가능한 행동임.")
            agent.push_think_event(ThinkEventType.PLANNING, f"'{invented_tool}' 시도 실패: {reject_reason}")
            world_system_manager.log_world_event(f"{agent.name}가 '{invented_tool}'을 시도했으나 실패함.")
            return

        tool_data = {
            "invented_tool": invented_tool,
            "creator": agent.name,
            "is_public": mediator_response.get("is_public", False),
            "description": description,
            "parameters": mediator_response.get("parameters", {}),
            "effects": mediator_response.get("effects", [])
        }
        
        is_registered = world_system_manager.dynamic_tool_manager.register_new_tool(tool_data)
        if is_registered:
            # 성공 피드백 주입
            success_msg = f"'{invented_tool}' 행동을 습득. 다음 행동부터 사용 가능."
            agent.push_think_event(ThinkEventType.PLANNING, success_msg)
            world_system_manager.log_world_event(f"{agent.name}가 '{invented_tool}'을 습득함.")
        else:
            # 이름이 중복되는 등 시스템적 거부 발생 시
            agent.push_think_event(ThinkEventType.PLANNING, f"'{invented_tool}'은 이미 알고 있거나 누군가 선점한 행동임.")