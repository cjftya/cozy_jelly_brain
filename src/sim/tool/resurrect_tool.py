from sim.tool.base_tool import BaseTool
from sim.tool.tool_type import ToolType
from sim.action.remove_action import RemoveAction

class ResurrectTool(BaseTool):
    def __init__(self):
        super().__init__("resurrect", ToolType.RESURRECT)

    def get_description(self):
        return (
            "[알렌 부활 권능] 4대 아티팩트('금기된 영혼 연성 마도서', '운명의 푸른 장미 줄기', '인과율의 균열 나침반', '성운의 핵 파편') 를 모두 모아 '마나 공명 제단'에서만 격발 가능. "
            "대가로 알렌에 대한 모든 기억 그래프가 영구 소멸함. "
            "부활 집행 시 'SKILL' 툴을 통한 마법 창조를 절대 금지하며, 반드시 이 'resurrect' 기능을 직접 호출할 것."
        )
        
    def get_params(self):
        return ''

    def execute(self, params, agent, world_system_manager):
        current_loc = agent.location_delegate.get_current_location()
        
        if current_loc != "마나 공명 제단":
            world_system_manager.log_world_event(f"{agent.name}가 제단이 아닌 곳에서 부활을 시도했으나 차가운 인과율의 침묵만이 있음.")
            return

        required_items = [
            "금기된 영혼 연성 마도서",
            "인과율의 균열 나침반",
            "운명의 푸른 장미 줄기",
            "성운의 핵 파편"
        ]
        
        item_set = {}
        for obj in agent.inventory.get_objects():
            item_set[obj.name] = obj.id

        if not all(item in item_set for item in required_items):
            missing_items = [item for item in required_items if item not in item_set]
            world_system_manager.log_world_event(f"{agent.name}가 부활을 위해 {', '.join(missing_items)}를 찾고 있으나, 인벤토리에 존재하지 않아 찾을 수 없습니다.")
            return

        # ==========================================
        # 조건 충족: 금기 파괴 및 부활 시퀀스 집행
        # ==========================================
        world_system_manager.log_world_event(f"4대 아티팩트를 소모하여 인과율을 역류시킴")

        # 재료 강제 영구 소멸 처리
        remove_action = RemoveAction(world_system_manager=world_system_manager)
        for item_name in required_items:
            remove_action.execute(item_set[item_name])

        # 대가 지불: 아스트리 레이아의 Kuzu DB 내부 '알렌' 관련 기억 청소 (Memory Wipe)
        agent.before_action = None
        agent.before_action_reason = None
        try:
            memory_db = agent.engine.core_memory
            # Kuzu DB 커넥션을 직접 제어하여 '알렌' 혹은 'ALLEN'이 포함된 노드와 시냅스(관계) 테이블을 물리적으로 완전 삭제
            memory_db.conn.execute("MATCH (n:node)-[r:rel]->(o:node) WHERE n.id = '알렌' OR o.id = '알렌' OR n.id = 'ALLEN' OR o.id = 'ALLEN' DELETE r")
            memory_db.conn.execute("MATCH (n:node) WHERE n.id = '알렌' OR n.id = 'ALLEN' DELETE n")
            world_system_manager.log_system_event("아스트리 레이아의 JellyBrain 시냅스 메모리 내 '알렌' 엔티티 및 유대 트리플렛 영구 삭제 완료.")
        except Exception as e:
            world_system_manager.log_system_event(f"메모리 삭제 중 예외 발생 (헤드리스 무결성 유지): {e}")

        # 대가 지불: 신체적 패널티
        agent.vital_state.update_health(80)
        agent.vital_state.update_fatigue(80)

        agent.tool_delegate.add_all_available_tool_types([
            ToolType.SPEAK, ToolType.GIVE
        ])

        # 알렌 에이전트 눈뜨기
        allen = world_system_manager.agent_manager.get_agent_by_name("ALLEN")
        if allen:
            allen.vital_state.is_alive = True
            allen.vital_state.update_health(100)
            allen.vital_state.update_fatigue(0)
            world_system_manager.log_world_event(f"'절 동결의 온실' 중앙의 얼음 결계가 산산조각 나며, 알렌이 200년 만에 깊은 숨을 몰아쉬며 다시 눈을 뜸.")
        else:
            world_system_manager.log_system_event("오류: 월드 내에서 '알렌' 에이전트 인스턴스를 찾을 수 없음.")