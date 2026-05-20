import random

class EventType:
    NO_EVENT = 0
    HUNGER_TRIPPED = 1
    FATIGUE_TRIPPED = 2
    RANDOM_SCAN = 3

class ThinkEventType:
    NO_EVENT = 0
    FIND_ITEM = 1
    FIND_AGENT = 2
    SPEAK = 3
    HUNGER = 4
    FATIGUE = 5
    SEARCH = 6
    

class EventTrigger:
    def __init__(self):
        self.turns_since_last_thought = 0

    def check_triggers(self, agents, current_weather):
        self.turns_since_last_thought += 1

        event_pack = []
        
        # 신체적 결핍 트리거
        for agent in agents:
            vital = agent.get_vital_state()
            if vital.hunger >= 80.0:
                self.turns_since_last_thought = 0
                event_pack.append([agent, EventType.HUNGER_TRIPPED, "[EXTERNAL_SIGNAL: 생체 위기] 배고픔이 한계에 달해 속이 쓰리고 고통스럽다."])

            if vital.fatigue >= 80.0:
                self.turns_since_last_thought = 0
                event_pack.append([agent, EventType.FATIGUE_TRIPPED, "[EXTERNAL_SIGNAL: 생체 위기] 극심한 피로로 인해 눈꺼풀이 무겁고 정신이 흐려진다."])

        if len(event_pack) > 0:
            return event_pack

        # 랜덤/주기적 외부 스캔 트리거
        if self.turns_since_last_thought >= 3 or random.random() < 0.1:
            self.turns_since_last_thought = 0
            return event_pack.append([None, EventType.RANDOM_SCAN, "[EXTERNAL_SIGNAL: 환경 스캔] 주변 환경을 확인하라."])

        return event_pack.append([None, EventType.NO_EVENT, None])


                