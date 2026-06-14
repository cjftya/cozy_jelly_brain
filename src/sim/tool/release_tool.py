import logging
from sim.tool.base_tool import BaseTool
from sim.tool.tool_type import ToolType
from sim.world.event_trigger import ThinkEventType

class ReleaseTool(BaseTool):

    def __init__(self):
        super().__init__("release", ToolType.RELEASE)

    def get_params(self):
        return ''

    def get_description(self):
        return "[조건: '별의 심연 절벽' 위치 & 인벤토리에 '별의 모래시계' 소지]. 알렌을 안식으로 보내는 최종 엔딩 권능 (호출 시 시뮬레이션 즉시 종료)."

    def execute(self, params, agent, world_system_manager):
        # 1. 공간적 제약 조건 검증 ('별의 심연 절벽' 위치 여부)
        current_location = agent.location_delegate.get_current_location()
        if "별의 심연 절벽" not in str(current_location):
            world_system_manager.log_world_event(f"[{agent.name}] 안식 권능 실패: 현재 위치({current_location})가 '별의 심연 절벽'이 아님.")
            agent.push_think_event(ThinkEventType.PLANNING, "'별의 심연 절벽'이 아니라서 안식을 실행할 수 없다. 이동 계획을 세운다.")
            return

        # 2. 필수 자원 제약 조건 검증 ('별의 모래시계' 보유 여부)
        has_hourglass = agent.inventory.has_object("별의 모래시계")
        if not has_hourglass:
            world_system_manager.log_world_event(f"[{agent.name}] 안식 권능 실패: 인벤토리에 '별의 모래시계'가 없습니다.")
            agent.push_think_event(ThinkEventType.PLANNING, "'별의 모래시계'가 없어서 안식을 실행할 수 없다. '별의 모래시계' 획득 계획을 세운다.")
            return

        # 3. 모든 제약 조건 통과 ➔ 최종 안식 엔딩 시퀀스 격발
        world_system_manager.log_world_event(f"[능동적 운명 개척] {agent.name}가 절벽 위에서 시간의 입자를 담은 별의 모래시계를 펼쳐들자, 알렌의 영혼을 붙잡던 마나의 실타래가 고요하게 풀려나며 빛의 파편으로 흩어짐. 마침내 기사 알렌의 헌신이 완전한 안식으로 승화됨.")
        agent.push_think_event(ThinkEventType.PLANNING, "안식을 성공적으로 수행했다. 이제 성운의 탑을 떠날 준비를 한다.")