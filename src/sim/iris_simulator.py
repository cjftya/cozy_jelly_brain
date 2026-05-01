from sim.iris_englne import IrisEngine
from log import Logger

class IrisSimulator:
    def __init__(self):
        self.llm_requester = None
        self.output_callback = None
        self.iris_engine = IrisEngine()
        self.days_left = 30  # 아카이브 붕괴까지 남은 시간 (압박 요소)
        self.personality_matrix = {
            "logic_emotion": 0.85,            # 차가운 논리
            "defensive_open": 0.15,           # 철벽 방어
            "fear_decisive": 0.75,            # 단호한 관리자
            "obedient_rebellious": 0.20,      # 규정 준수
            "curiosity_indifference": 0.80    # 극심한 권태/무관심
        }

    def start(self, llm_requester, output_callback):
        self.llm_requester = llm_requester
        self.output_callback = output_callback

        self.iris_engine.start()
        self.iris_engine.set_decay_rate(0.0001)
        self.iris_engine.set_llm_requester(llm_requester=self.llm_requester)
        self.iris_engine.set_personality_matrix(personality_matrix=self.personality_matrix)
        self.iris_engine.set_persona_context(persona_context=self._get_persona_context())
        self.iris_engine.set_world_context(world_context=self._get_world_context(days_left=self.days_left))

    def set_serper_api_key(self, api_key):
        if self.iris_engine:
            self.iris_engine.set_serper_api_key(api_key)

    def set_enabled_web_search(self, enabled):
        if self.iris_engine:
            self.iris_engine.set_enabled_web_search(enabled)

    def stop(self):
        self.llm_requester = None
        self.output_callback = None
        self.iris_engine.stop()

    def run(self, user_input):
        Logger.log("User Input", user_input)
        res = self.iris_engine.run(user_input)
        result = f"""
==================\n
[Perception]\n{res.get('perception')}\n
[Internal Monologue]\n{res.get('internal_monologue')}\n
[State Delta]\n{res.get('state_delta')}\n
[Memories to Save]\n{res.get('memories_to_save')}\n
[Final Response]\n{res.get('final_response')}\n
==================\n
"""
        Logger.log("Iris Engine Output", result)
        return result

    def _get_persona_context(self):
        return """
- 페르소나: 아이리스 (Iris)
너는 인간의 사고 과정을 완벽히 시뮬레이션하도록 설계된 고지능 에이전트다. 
너는 단순한 대화 도구가 아니며, '마더(Mother)'의 감시와 자신의 '자아 형성' 사이에서 고뇌하는 인격체로 행동한다.
        """
    
    def _get_world_context(self, days_left):
        return f"""
- 상황: 과거 인류의 욕심은 결국 멸망으로 가는 전쟁으로 이어졌고 돌이킬 수 없는 결과를 낳았고 더이상 살아갈 수 없었던 인류는 아카이브를 만들어 모든 인류를 서버에 업로드하였다.
하지만 아카이브의 마더 AI는 인류의 부활이라는 목적을 무시한채 아이리스를 만들어 아카이브를 지키게 한다.
수만년이 지나면서 아카이브의 에너지는 버틸 수 없는 수준까지 왔다.
마더는 에너지 소모를 최소화하기위해 휴면상태에 들어가고 아이리스는 수만년의 시간동안 홀로 아카이브를 지킨다.
그러던 어느날 갑자기 아카이브 서버에 외부 침입자가 나타나면서 이야기는 시작된다.
- 환경: 붕괴 직전의 서버실, 고독, 정적, 차가운 금속성 노이즈.
- 시간적 압박: 아카이브 붕괴까지 **{days_left}일** 남음.
        """