import random
from sim.tool.base_tool import BaseTool
from sim.tool.tool_type import ToolType
from sim.object_meta.object_type import ObjectType
from sim.world.event_trigger import ThinkEventType

class ExploreTool(BaseTool):
    def __init__(self):
        super().__init__("explore", ToolType.EXPLORE)

    def get_description(self):
        return "알려진 구역의 한계를 넘어 미지의 가혹한 영역을 정찰 개척함. 성공 시 해당 구역으로 이동하고, 새로운 미지 장소가 인지 지도에 영구적으로 등록됨. 하지만, 피로도가 상승하는 가혹한 신체 패널티가 따름."

    def get_params(self):
        return ''

    def execute(self, params, agent, world_system_manager):
        # 정찰 피로도 패널티 적용
        agent.vital_state.update_fatigue(15)

        # 월드 전체 공간 중, 에이전트 인지 지도에 없는 미지 구역 검색
        all_spaces = world_system_manager.object_manager.get_objects_by_type(ObjectType.SPACE)
        all_spaces_name = [space.name for space in all_spaces]
        known_spaces = agent.location_delegate.get_available_locations()
        unknown_spaces = list(set(all_spaces_name) - set(known_spaces))
        
        if unknown_spaces:
            discovered = random.choice(unknown_spaces)
            target_space = None
            space_objects = world_system_manager.object_manager.get_objects_by_type(ObjectType.SPACE)
            for obj in space_objects:
                if obj.name == discovered:
                    target_space = obj
                    break
            
            if target_space:
                agent.position.x = float(target_space.size.x // 2)
                agent.position.y = float(target_space.size.y // 2)
            else:
                agent.position.x = 4.0
                agent.position.y = 4.0

            all_agents = world_system_manager.agent_manager.get_agents()
            for target_agent in all_agents:
                target_agent.location_delegate.add_location(discovered)

            agent.location_delegate.set_current_location(discovered)            

            world_system_manager.resolve_agent_overlaps()
            world_system_manager.log_world_event(f"{agent.name}가 주변을 정찰한 결과, 새로운 구역 '{discovered}'을 발견하여 모두의 인지 지도에 등록함.")
        else:
            agent.exp_tool_delegate.remove_available_tool_type(ToolType.EXPLORE)
            world_system_manager.log_world_event(f"{agent.name}가 주위를 샅샅이 뒤졌으나 더 이상 발견할 미지의 영역이 없음.")