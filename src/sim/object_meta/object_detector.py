import math
from sim.util.point import Point
from sim.object_meta.object_type import ObjectType

class ObjectDetector:
    def __init__(self, base_range=10.0, view_angle=90.0):
        self.base_range = base_range    # 기본 시야 거리
        self.view_angle = view_angle    # 시야각 (전방 90도)

    def _calculate_dynamic_range(self, matrix, vital_state):
        """
        에이전트의 상태에 따라 시야 거리를 동적으로 계산
        """
        # 1. fear_decisive (낮을수록 공포/우유부단 -> 터널 비전 발생으로 시야 급감)
        # matrix가 없거나 값이 없으면 기본값 0.5
        fear_decisive = matrix.get('fear_decisive', 0.5) if matrix else 0.5
        # 공포 수치가 극대화(0에 수렴)되면 시야 거리가 최대 70%까지 감소
        fear_factor = 0.3 + 0.7 * fear_decisive 

        # 2. fatigue (높을수록 시야 감소, vital_state.fatigue는 0~100 사이로 가정)
        fatigue = vital_state.fatigue if hasattr(vital_state, 'fatigue') else 0
        fatigue_factor = 1.0 - (min(fatigue, 100) / 100.0 * 0.5) # 피로도 맥스 시 시야 50% 감소

        # 3. curiosity_indifference (낮을수록 호기심 많음 -> 범위 넓음)
        curiosity_indifference = matrix.get('curiosity_indifference', 0.5) if matrix else 0.5
        curiosity_factor = 1.3 - (curiosity_indifference * 0.5) # 호기심이 많을수록(0에 가까울수록) 보너스

        # 최종 동적 시야 거리 계산
        dynamic_range = self.base_range * fear_factor * fatigue_factor * curiosity_factor
        return dynamic_range

    def detect_agents(self, agent, all_agents):
        return self._detect_entities(agent, [a for a in all_agents if a.vital_state.is_alive])

    def detect_objects(self, agent, world_objects):
        return self._detect_entities(agent, [a for a in world_objects if a.type == ObjectType.ITEM])

    def _detect_entities(self, agent, entities):
        if len(entities) <= 1:
            return []

        detected_list = []
        agent_pos = agent.position
        agent_dir = getattr(agent, 'direction', 'N')
        current_range = self._calculate_dynamic_range(agent.personality_matrix, agent.vital_state)

        dir_vectors = {"N": (0.0, 1.0), "S": (0.0, -1.0), "E": (1.0, 0.0), "W": (-1.0, 0.0)}
        forward_vector = dir_vectors.get(agent_dir, (0.0, 1.0))

        for entity in entities:
            if hasattr(entity, 'id') and entity.id == agent.id:
                continue

            dx = entity.position.x - agent_pos.x
            dy = entity.position.y - agent_pos.y
            distance = math.sqrt(dx**2 + dy**2)

            if distance > current_range: continue
            if distance == 0:
                detected_list.append(entity)
                continue

            obj_unit_x = dx / distance
            obj_unit_y = dy / distance

            dot_product = max(-1.0, min(1.0, (forward_vector[0] * obj_unit_x) + (forward_vector[1] * obj_unit_y)))
            if math.degrees(math.acos(dot_product)) <= (self.view_angle / 2.0):
                detected_list.append(entity)

        return detected_list