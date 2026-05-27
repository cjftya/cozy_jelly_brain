import random
from sim.tool.base_tool import BaseTool
from sim.tool.tool_type import ToolType
from sim.object_meta.object_type import ObjectType

class ExploreTool(BaseTool):
    def __init__(self):
        super().__init__("explore", ToolType.EXPLORE)

    def get_description(self):
        return "알려진 구역의 한계를 넘어 미지의 가혹한 영역을 정찰 개척함. 성공 시 이동 가능한 새로운 미지 장소가 인지 지도에 영구 해금되지만, 피로도가 대폭 상승하는 가혹한 신체 패널티가 따름."

    def get_params(self):
        return ''

    def execute(self, params, agent, world_system_manager):
        # 가혹한 정찰 피로도 패널티 적용
        agent.vital_state.update_fatigue(55)
        agent.vital_state.update_hunger(30)

        # 월드 전체 공간 중, 에이전트 인지 지도에 없는 미지 구역 검색
        all_spaces = world_system_manager.object_manager.get_objects_by_type(ObjectType.SPACE)
        all_spaces_name = [space.name for space in all_spaces]
        known_spaces = agent.location_delegate.get_available_locations()
        unknown_spaces = list(set(all_spaces_name) - set(known_spaces))
        
        if unknown_spaces:
            discovered = random.choice(unknown_spaces)
            agent.location_delegate.add_location(discovered)
            world_system_manager.log_world_event(f"{agent.name}가 가혹한 수풀을 헤치며 정찰한 결과, 새로운 구역 [{discovered}]을 발견하여 인지 지도에 등록함.")
        else:
            agent.exp_tool_delegate.remove_available_tool_type(ToolType.EXPLORE)
            world_system_manager.log_world_event(f"{agent.name}가 섬 주위를 샅샅이 뒤졌으나 더 이상 발견할 미지의 영역이 없음.")