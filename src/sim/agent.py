from sim.iris_engine import IrisEngine
from sim.agent_meta.participants_delegate import ParticipantsDelegate
from sim.agent_meta.location_delegate import LocationDelegate
from sim.agent_meta.vital_state import VitalState
from sim.util.point import Point
from sim.object_meta.object_manager import ObjectManager
from sim.util.globar_util import GlobarUtil

class Agent:
    def __init__(self, name="UNKNOWN", identifier="UNKNOWN"):
        self.id = GlobarUtil.gen_agent_id()
        self.name = name
        self.identifier = identifier

        # 인지 엔진
        self.llm_requester = None
        self.iris_engine = IrisEngine(self.name)

        # 생체 정보
        self.vital_state = VitalState()

        # 주변 에이전트 정보
        self.participants_delegate = ParticipantsDelegate()

        # 공간 정보
        self.location_delegate = LocationDelegate()

        # 인벤토리
        self.inventory = ObjectManager()

        # 좌표
        self.position = Point()

        # 성격 매트릭스
        # logic_emotion : 감성적인가 이성적인가
        # defensive_open : 방어적인가 개방적인가
        # fear_decisive : 공포에 우유부단한가 용감하고 단호한가
        # obedient_rebellious : 복종적인가 반항적인가
        # curiosity_indifference : 호기심이 많은가 무관심한가
        self.personality_matrix = self.get_personality_matrix()

        # 관계 정보
        self.relationship_map = {}

    def start(self, llm_requester):
        self.llm_requester = llm_requester
        self.iris_engine.start(llm_requester)

    def stop(self):
        self.llm_requester = None
        self.iris_engine.stop()
    
    def run(self, user_input):
        res = self.iris_engine.run(user_input, self)
        return res

    def set_serper_api_key(self, api_key):
        if self.iris_engine:
            self.iris_engine.set_serper_api_key(api_key)

    def support_web_search(self):
        return False

    def get_personality_matrix(self):
        return None

    def get_persona_context(self):
        return None
    
    def get_world_context(self):
        return None

    def get_response_style(self):
        return None

    def get_intrinsic_desires(self):
        return None

    def get_relationships(self):
        if not self.relationship_map:
            return "식별된 관계 데이터가 없음."

        return "\n".join([f"- {name}: {score}" for name, score in self.relationship_map.items()])

    def get_location_delegate(self):
        return self.location_delegate

    def get_participant_delegate(self):
        return self.participants_delegate

    def get_vital_state(self):
        return self.vital_state

    def get_inventory(self):
        return self.inventory