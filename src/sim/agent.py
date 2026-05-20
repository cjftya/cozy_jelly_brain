import random
from sim.iris_engine import IrisEngine
from sim.agent_meta.participants_delegate import ParticipantsDelegate
from sim.agent_meta.location_delegate import LocationDelegate
from sim.agent_meta.vital_state import VitalState
from sim.util.point import Point
from sim.object_meta.object_detector import ObjectDetector
from sim.object_meta.object_manager import ObjectManager
from sim.world.world_context_manager import WorldContextManager
from sim.util.global_util import GlobalUtil
from sim.world.event_trigger import ThinkEventType

class Agent:
    def __init__(self, name="UNKNOWN", identifier="UNKNOWN", world_context_manager: WorldContextManager=None):
        self.id = GlobalUtil.gen_agent_id()
        self.name = name
        self.identifier = identifier

        # LLM 트리거
        self.enable_thinking = False

        # Think Event 큐
        self.think_event_queue = {}

        # 월드 컨텍스트 매니져
        self.world_context_manager = world_context_manager

        # 인지 엔진
        self.llm_requester = None
        self.iris_engine = IrisEngine(self.name, self.world_context_manager)

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
        self.direction = "S"  # 초기값: 남쪽 (N/S/E/W)
        
        # 시야 감지 엔진
        self.object_detector = ObjectDetector()

        # 성격 매트릭스 (0 ~ 1.0)
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

    def scan(self, external_event):
        found_agents = self.perceive_agents()
        found_objects = self.perceive_objects()
        if len(found_agents) <= 0 and len(found_objects) <= 0:
            return

        if len(found_agents) > 0 and self.vital_state.fatigue < 70 and self.vital_state.health > 30:
            ran_num = self.personality_matrix['defensive_open'] + random.random()
            if ran_num >= 1.0:
                self.push_think_event(ThinkEventType.FIND_AGENT, external_event + " 주변에 대화할만한 대상이 있다.", found_agents)

        if len(found_objects) > 0:
            self.push_think_event(ThinkEventType.FIND_ITEM, external_event + " 주위에 관심있는 사물이 있다.", found_objects)

    def push_think_event(self, think_event_type, message, data=None):
        self.set_enable_thinking(True)
        self.think_event_queue[think_event_type] = {"message":message, "data":data}
    
    def tick(self, time_scale):
        self.vital_state.tick(time_scale)

    def think_tick(self):
        if not self.enable_thinking:
            return None

        # release think_state
        self.set_enable_thinking(False)

        # body signal
        if any([event_type in self.think_event_queue.keys() for event_type in [ThinkEventType.FATIGUE, ThinkEventType.HUNGER]]):
            event_type_list = [ThinkEventType.FATIGUE, ThinkEventType.HUNGER]
            combined_signal = ""
            for event_type in event_type_list:
                if event_type in self.think_event_queue.keys():
                    think_event = self.think_event_queue[event_type]
                    think_event_message = think_event.get("message", "")
                    think_event_data = think_event.get("data", None)
                    combined_signal += f"{think_event_message}\n"

            self.think_event_queue.clear()
            res = self.iris_engine.event(agent=self, event_type=None, external_event=combined_signal, available_tools=self.get_available_tools(False))
            return res

        # find agent signal
        if ThinkEventType.FIND_AGENT in self.think_event_queue.keys():
            think_event = self.think_event_queue[ThinkEventType.FIND_AGENT]
            think_event_message = think_event.get("message", "")
            found_agents = think_event.get("data", None)

            self.think_event_queue.clear()
            res = self.iris_engine.speak(user_input=think_event_message, agent=self, available_agents=found_agents, from_scan=True, available_tools=self.get_available_tools(True))
            return res

        # find item signal
        if ThinkEventType.FIND_ITEM in self.think_event_queue.keys():
            think_event = self.think_event_queue[ThinkEventType.FIND_ITEM]
            think_event_message = think_event.get("message", "")
            found_objects = think_event.get("data", None)

            self.think_event_queue.clear()
            res = self.iris_engine.search(agent=self, external_event=think_event_message, detected_objects=found_objects, available_tools=self.get_available_tools(False))
            return res
        
        # speak signal
        if ThinkEventType.SPEAK in self.think_event_queue.keys():
            think_event = self.think_event_queue[ThinkEventType.SPEAK]
            think_event_message = think_event.get("message", "")
            found_agent_name = think_event.get("data", None)
            user_input = f"[From {found_agent_name}] : {think_event_message}"
            available_agent = self.world_context_manager.agent_manager.get_agent_by_name(found_agent_name)

            self.think_event_queue.clear()
            res = self.iris_engine.speak(user_input=user_input, agent=self, available_agents=[available_agent], from_scan=False, available_tools=self.get_available_tools(True))
            return res

        # event signal
        combined_signal = ""
        for think_event_type, think_event in self.think_event_queue.items():
            # 이벤트에 따라서 조합을 커스텀 할 수 있음
            think_event_message = think_event.get("message", "")
            combined_signal += f"{think_event_message}\n"
        self.think_event_queue.clear()
        res = self.iris_engine.event(agent=self, event_type=None, external_event=combined_signal, available_tools=self.get_available_tools(False))
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

    def get_available_tools(self, is_dialogue_mode):
        if is_dialogue_mode:
            return ["speak", "give", "none"]
        else:
            return ["take", "move_to", "search", "use", "rest", "none"]

    def perceive_agents(self):
        all_agents = self.world_context_manager.agent_manager.get_agents()
        detected_agents = self.object_detector.detect_agents(self, all_agents)
        return detected_agents

    def perceive_objects(self):
        world_objects = self.world_context_manager.object_manager.get_objects()
        detected_entities = self.object_detector.detect_objects(self, world_objects)
        return detected_entities
    
    def perform_brain_cleanup(self):
        self.iris_engine.perform_brain_cleanup()

    def set_enable_thinking(self, enable):
        self.enable_thinking = enable