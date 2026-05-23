import math
from sim.util.point import Point
from sim.object_meta.object_type import ObjectType

class ObjectDetector:
    def __init__(self, base_range=10.0, view_angle=360.0):
        self.base_range = base_range    # 기본 시야 거리
        self.view_angle = view_angle    # 시야각 (360도로 변경하여 전방위 감지)

    def _calculate_dynamic_range(self, matrix, vital_state):
        # 1. fear_decisive (낮을수록 공포/우유부단 -> 터널 비전 발생으로 시야 급감)
        fear_decisive = matrix.get('fear_decisive', 0.5) if matrix else 0.5
        # 공포 수치가 극대화(0에 수렴)되면 시야 거리가 최대 70%까지 감소
        fear_factor = 0.3 + 0.7 * fear_decisive 

        # 2. fatigue (높을수록 시야 감소)
        fatigue = vital_state.fatigue if hasattr(vital_state, 'fatigue') else 0
        fatigue_factor = 1.0 - (min(fatigue, 100) / 100.0 * 0.5) # 피로도 맥스 시 시야 50% 감소

        # 3. curiosity_indifference (낮을수록 호기심 많음 -> 범위 넓음)
        curiosity_indifference = matrix.get('curiosity_indifference', 0.5) if matrix else 0.5
        curiosity_factor = 1.3 - (curiosity_indifference * 0.5) # 호기심이 많을수록 보너스

        # 최종 동적 시야 거리 계산
        dynamic_range = self.base_range * fear_factor * fatigue_factor * curiosity_factor
        return dynamic_range

    def detect_agents(self, agent, all_agents):
        agents_list = [a for a in all_agents if a.vital_state.is_alive]
        if len(agents_list) == 1 and agent.id == agents_list[0].id:
            return []

        return self._detect_entities(agent, agents_list)

    def detect_objects(self, agent, world_objects):
        current_room_name = agent.location_delegate.get_current_location()
        objects_list = [
            o for o in world_objects 
            if o.type == ObjectType.ITEM 
            and o.parent is not None 
            and o.parent.name == current_room_name
        ]
        return self._detect_entities(agent, objects_list)

    def _detect_entities(self, agent, entities):
        if len(entities) == 0:
            return []

        detected_list = []
        agent_pos = agent.position
        current_range = self._calculate_dynamic_range(agent.personality_matrix, agent.vital_state)

        for entity in entities:
            if hasattr(entity, 'id') and entity.id == agent.id:
                continue

            dx = entity.position.x - agent_pos.x
            dy = entity.position.y - agent_pos.y
            distance = math.sqrt(dx**2 + dy**2)
            if distance > current_range: 
                continue
                
            detected_list.append(entity)

        return detected_list