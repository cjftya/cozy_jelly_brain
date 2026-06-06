import random

class EventType:
    NO_EVENT = 0
    HUNGER_TRIPPED = 1
    FATIGUE_TRIPPED = 2
    RANDOM_SCAN = 3
    PROACTIVE_PULSE = 4
    CRITICAL_PULSE = 5

class ThinkEventType:
    NO_EVENT = 0
    FIND_ITEM = 1
    FIND_AGENT = 2
    SPEAK = 3
    HUNGER = 4
    FATIGUE = 5
    INSPECT = 6
    PLANNING = 7
    WEB_SEARCH = 8
    DYNAMIC_TOOL_FEEDBACK = 9

class EventTrigger:
    def __init__(self):
        self.move_timer = 0
        self.scan_timer = 0
        self.plan_timer = 0
        self.hunger_alert_timer = 999.0
        self.fatigue_alert_timer = 999.0

    def stop(self):
        self.move_timer = -99999
        self.scan_timer = -99999
        self.plan_timer = -99999
        self.hunger_alert_timer = -99999.0
        self.fatigue_alert_timer = -99999.0
    
    def check_triggers(self, agents, time_scale=1.0):
        self.move_timer += time_scale
        self.scan_timer += time_scale
        self.plan_timer += time_scale
        self.hunger_alert_timer += time_scale
        self.fatigue_alert_timer += time_scale

        event_pack = []

        PLAN_INTERVAL = 20 / 60.0  # 인게임 기준 '20분' 마다 확실한 기획 제공
        MOVE_INTERVAL = 12 / 60.0  # 인게임 기준 최소 '12분' 정체 시 충동 검사
        SCAN_INTERVAL = 15 / 60.0  # 인게임 기준 '15분' 마다 스캔 검사
        VITAL_ALERT_COOLDOWN = 10 / 60.0 # 인게임 기준 '10분' 재경고 가드

        # 신체적 결핍 트리거
        for agent in agents:
            if agent.is_thinking:
                continue

            vital = agent.vital_state
            
            if vital.hunger >= 80.0 and self.hunger_alert_timer >= VITAL_ALERT_COOLDOWN:
                self.hunger_alert_timer = 0.0
                self.plan_timer = 0.0
                
                msg = "[EXTERNAL_SIGNAL: 생체 위기] 에너지 결핍이 위험 수준(>=80%). 가용 자원 상황과 궁극적 목표의 시급성을 대조하여, 에너지 충전과 목표 강행 중 최선의 전략을 판단하고 결단할 것."
                event_pack.append([agent, EventType.HUNGER_TRIPPED, msg])
                return event_pack

            if vital.fatigue >= 80.0 and self.fatigue_alert_timer >= VITAL_ALERT_COOLDOWN:
                self.fatigue_alert_timer = 0.0
                self.plan_timer = 0.0
                
                msg = "[EXTERNAL_SIGNAL: 생체 위기] 누적 피로도가 위험 수준(>=80%). 무리한 행동 지속은 자멸 위험이 있으나 필수 과제가 있다면 인내할 수 있음. 즉시 휴식할지, 위험을 무릅쓰고 강행할지 결단할 것."
                event_pack.append([agent, EventType.FATIGUE_TRIPPED, msg])
                return event_pack

        # 독립된 계획 신호
        if self.plan_timer >= PLAN_INTERVAL:
            self.plan_timer = 0
            for agent in agents:
                if agent.is_thinking:
                    continue

                # 모든 에이전트를 추가하면 안되고 랜덤하게 추가하도록
                if random.random() < 0.4:
                    event_pack.append([agent, EventType.PROACTIVE_PULSE, "[EXTERNAL_SIGNAL: 자율 계획] 현재 상황을 종합적으로 분석하고, 당신의 궁극적인 목표를 달성하기 위한 단계별 행동 전략을 수립하라."])
            return event_pack

        # 고립 탈출 신호
        if self.move_timer >= MOVE_INTERVAL and random.random() < 0.1:
            self.move_timer = 0
            for agent in agents:
                if agent.is_thinking:
                    continue
                
                if random.random() < 0.3:
                    event_pack.append([agent, EventType.CRITICAL_PULSE, "[EXTERNAL_SIGNAL: 위기 탈출] 현재 상황이나 행동 루틴에서 더 이상 새로운 진전이 없는 것 같다. 고착된 상태를 깨고, 다음 단계나 새로운 돌파구를 모색해야겠다는 생각이 든다."])
            return event_pack

        # 스캔 신호
        if self.scan_timer >= SCAN_INTERVAL and random.random() < 0.08:
            self.scan_timer = 0
            event_pack.append([None, EventType.RANDOM_SCAN, "[EXTERNAL_SIGNAL: 환경 스캔] 주변 환경을 확인하라."])
            return event_pack

        return event_pack