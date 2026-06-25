from sim.object_meta.object_type import ObjectType
from sim.tool.base_tool import BaseTool
from sim.tool.tool_type import ToolType


class MoveTool(BaseTool):
    def __init__(self):
        super().__init__("move_to", ToolType.MOVE_TO)

    def get_description(self):
        return "공간적 위치(좌표)를 다른 구역으로 이동."

    def get_params(self):
        return '{"location": "Available Locations 중 하나"}'

    def execute(self, params, agent, world_system_manager):
        location = params.get("location", None)
        if location and location in agent.location_delegate.get_available_locations():
            # 문자열 상태 정보 업데이트
            agent.location_delegate.set_current_location(location)

            # 무한 확장 절대 좌표계를 고려한 로컬 좌표 초기화
            target_space = None
            space_objects = world_system_manager.object_manager.get_objects_by_type(
                ObjectType.SPACE
            )
            for obj in space_objects:
                if obj.name == location:
                    target_space = obj
                    break

            # 방의 규격(size) 정보를 찾았다면 정중앙 로컬 좌표계로 자동 세팅
            if target_space and hasattr(target_space, "size"):
                agent.position.x = float(target_space.size.x // 2)
                agent.position.y = float(target_space.size.y // 2)
            else:
                # 방 오브젝트 누락 예외를 대비한 기본 방어 좌표
                agent.position.x = 4.0
                agent.position.y = 4.0

            world_system_manager.resolve_agent_overlaps()
            world_system_manager.log_world_event(
                f"{agent.name}가 {location} 공간으로 이동."
            )
        else:
            world_system_manager.log_world_event(
                f"{agent.name}가 {location} 공간으로 이동할 수 없음."
            )
