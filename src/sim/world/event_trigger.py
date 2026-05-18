class EventType:
    NO_EVENT = 0
    WEATHER_CHANGE = 1
    HUNGER_TRIPPED = 2
    FATIGUE_TRIPPED = 3
    RANDOM_SCAN = 4

class EventTrigger:
    def __init__(self):
        self.last_weather = None
        self.turns_since_last_thought = 0

    def check_triggers(self, agents, current_weather):
        self.turns_since_last_thought += 1
        
        # [우선순위 1위] 외부 이벤트 트리거 (날씨 급변)
        if self.last_weather is not None and current_weather != self.last_weather:
            self.last_weather = current_weather
            if current_weather in ["비", "눈", "천둥", "번개"]:
                self.turns_since_last_thought = 0
                return [None, EventType.WEATHER_CHANGE, f"[EXTERNAL_SIGNAL: 환경 급변] 날씨가 급격하게 {current_weather}(으)로 변했다. 이에 대응하라."]
        self.last_weather = current_weather

        # [우선순위 2위] 신체적 결핍 트리거
        agent_array = []
        for agent in agents:
            vital = agent.get_vital_state()
            if vital.hunger >= 80.0:
                self.turns_since_last_thought = 0
                agent_array.append([agent, EventType.HUNGER_TRIPPED, "[EXTERNAL_SIGNAL: 생체 위기] 배고픔이 한계에 달해 속이 쓰리고 고통스럽다."])

            if vital.fatigue >= 80.0:
                self.turns_since_last_thought = 0
                agent_array.append([agent, EventType.FATIGUE_TRIPPED, "[EXTERNAL_SIGNAL: 생체 위기] 극심한 피로로 인해 눈꺼풀이 무겁고 정신이 흐려진다."])

        if len(agent_array) > 0:
            return agent_array

        # [우선순위 3위] 고민하셨던 랜덤/주기적 외부 스캔 트리거
        # 평화로운 상태로 3턴 이상 방치되었거나, 일정 확률로 주변을 인지하고 싶을 때
        if self.turns_since_last_thought >= 3 or random.random() < 0.1:
            self.turns_since_last_thought = 0
            return [None, EventType.RANDOM_SCAN, "[EXTERNAL_SIGNAL: 일상 스캔] 주변 환경을 환기하고 현재 상태를 점검하여 다음 행동을 결정하라."]

        return [None, EventType.NO_EVENT, None]


                