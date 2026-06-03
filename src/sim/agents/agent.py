import random
from sim.core.jelly_engine import JellyEngine
from sim.agent_meta.participants_delegate import ParticipantsDelegate
from sim.agent_meta.location_delegate import LocationDelegate
from sim.agent_meta.tool_delegate import ToolDelegate
from sim.agent_meta.vital_state import VitalState
from sim.agent_meta.personality_matrix import PersonalityMatrix
from sim.agent_meta.relationship_score_matrix import RelationShipScoreMatrix
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sim.world.world_system_manager import WorldSystemManager
from sim.world.event_trigger import ThinkEventType
from sim.world.weather_engine import WeatherType
from sim.world.time_engine import DayCycleType, SeasonType
from sim.util.object_detector import ObjectDetector
from sim.util.object_manager import ObjectManager, ObjectType
from sim.util.global_util import GlobalUtil
from sim.util.point import Point
from sim.tool.tool_type import ToolType
from sim.objects.atomic_object import AtomicObject

class Agent(AtomicObject):
    def __init__(self, name="UNKNOWN", identifier="UNKNOWN", world_system_manager: "WorldSystemManager"=None, brain_root_dir_path=None):
        super().__init__(name, GlobalUtil.gen_agent_id())
        self.identifier = identifier

        # LLM 트리거
        self.enable_thinking = False

        # Think Event 큐
        self.think_event_queue = {}

        # 이전 행동 정보
        self.before_action = "none"
        self.before_action_reason = ""

        # 월드 시스템 매니져
        self.world_system_manager = world_system_manager

        # 인지 엔진
        self.engine = JellyEngine(self.name, self.world_system_manager, brain_root_dir_path)

        # 생체 정보
        self.vital_state = VitalState()

        # 성격 매트릭스
        self.personality_matrix = PersonalityMatrix()

        # 관계 점수 매트릭스
        self.relationship_score_matrix = RelationShipScoreMatrix()

        # 주변 에이전트 정보
        self.participants_delegate = ParticipantsDelegate()

        # 공간 정보
        self.location_delegate = LocationDelegate()

        # 툴 정보
        self.tool_delegate = ToolDelegate()

        # 인벤토리
        self.inventory = ObjectManager()

        # 좌표
        self.position = Point()
        
        # 시야 감지 엔진
        self.object_detector = ObjectDetector()

        # 환경적 요인으로 인한 누적 변동치 (-0.15 ~ +0.15) 외부에서 사용되지않고 내부에서만 연동
        self.env_deltas = {
            'logic_emotion': 0.0,
            'defensive_open': 0.0,
            'fear_decisive': 0.0,
            'curiosity_indifference': 0.0,
            'obedient_rebellious': 0.0
        }

        self._init_personality_matrix(self.personality_matrix)
        self._init_tools(self.tool_delegate)

    def start(self, llm_requester):
        self.engine.start(llm_requester)

    def stop(self):
        self.engine.stop()
    
    def tick(self, time_scale):
        day_cycle = self.world_system_manager.time_engine.day_cycle
        weather_type = self.world_system_manager.weather_engine.weather_type

        self.vital_state.tick(time_scale)
        self._update_environmental_debuff(day_cycle=day_cycle, weather_type=weather_type, time_scale=time_scale)

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
            res = self.engine.think_event_normal(agent=self, event_type=None, external_event=combined_signal, available_tool_types=self.get_available_tool_types())
            return res

        # find agent signal
        if ThinkEventType.FIND_AGENT in self.think_event_queue.keys():
            think_event = self.think_event_queue[ThinkEventType.FIND_AGENT]
            think_event_message = think_event.get("message", "")
            found_agents = think_event.get("data", None)

            self.think_event_queue.clear()
            res = self.engine.think_event_speak(user_input=think_event_message, agent=self, available_agents=found_agents, from_scan=True, available_tool_types=self.get_available_tool_types())
            return res

        # find item signal
        if ThinkEventType.FIND_ITEM in self.think_event_queue.keys():
            think_event = self.think_event_queue[ThinkEventType.FIND_ITEM]
            think_event_message = think_event.get("message", "")
            found_objects = think_event.get("data", None)

            self.think_event_queue.clear()
            res = self.engine.think_event_detect_objects(agent=self, external_event=think_event_message, detected_objects=found_objects, available_tool_types=self.get_available_tool_types())
            return res
        
        # speak signal
        if ThinkEventType.SPEAK in self.think_event_queue.keys():
            think_event = self.think_event_queue[ThinkEventType.SPEAK]
            think_event_message = think_event.get("message", "")
            found_agent_name = think_event.get("data", None)
            user_input = f"[From {found_agent_name}] : {think_event_message}"
            available_agent = self.world_system_manager.agent_manager.get_agent_by_name(found_agent_name)

            self.think_event_queue.clear()
            res = self.engine.think_event_speak(user_input=user_input, agent=self, available_agents=[available_agent], from_scan=False, available_tool_types=self.get_available_tool_types())
            return res

        # event signal
        combined_signal = ""
        for think_event_type, think_event in self.think_event_queue.items():
            think_event_message = think_event.get("message", "")
            combined_signal += f"{think_event_message}\n"
        self.think_event_queue.clear()
        res = self.engine.think_event_normal(agent=self, event_type=None, external_event=combined_signal, available_tool_types=self.get_available_tool_types())
        return res

    def push_think_event(self, think_event_type, message, data=None):
        self.set_enable_thinking(True)
        self.think_event_queue[think_event_type] = {"message":message, "data":data}

    def clear_think_event(self):
        self.set_enable_thinking(False)
        self.think_event_queue.clear()

    def scan(self, external_event):
        found_agents = self.perceive_agents()
        found_objects = self.perceive_objects()
        if len(found_agents) <= 0 and len(found_objects) <= 0:
            return

        # 단일 난수 주사위를 굴려 행동 우선순위를 정함 (0.0 ~ 1.0)
        action_roll = random.random()
        matrix = self.get_personality_matrix().get_matrix()

        # [40% 확률 분기] 대상을 먼저 인지하는 경우
        if action_roll < 0.4 and len(found_agents) > 0:
            if len(found_agents) > 0 and self.vital_state.fatigue < 70 and self.vital_state.health > 30:
                ran_num = matrix["defensive_open"] + random.random()
                if ran_num >= 1.0:
                    msg = " 주변에 다른 상대가 보인다. 너의 신체적 겹핍, 목적 달성에 따라 대상을 무시하거나 말을 걸지 판단하라. 대화가 무의미하다면 억지로 'speak' 도구를 사용하지마라."
                    self.push_think_event(ThinkEventType.FIND_AGENT, external_event + msg, found_agents)
                    return
        
        # [60% 확률 분기] (또는 앞선 대인 인지 조건을 통과하지 못해 이쪽으로 넘어온 경우)
        if len(found_objects) > 0:
            msg = " 주위에 관심있는 사물이 있다. 너의 신체적 겹핍, 목적 달성에 따라 사물을 조사하거나 획득할지 결정하라."
            self.push_think_event(ThinkEventType.FIND_ITEM, external_event + msg, found_objects)
            return

    def _update_environmental_debuff(self, time_scale, day_cycle, weather_type):
        pass

    def set_serper_api_key(self, api_key):
        if self.engine:
            self.engine.set_serper_api_key(api_key)

    def support_web_search(self):
        return False

    def get_personality_matrix(self):
        return self.personality_matrix

    def get_persona_context(self):
        return None
    
    def get_world_context(self):
        return None

    def get_response_style(self):
        return None

    def get_intrinsic_desires(self):
        return None

    def get_relationships(self):
        return self.relationship_score_matrix

    def get_location_delegate(self):
        return self.location_delegate

    def get_participant_delegate(self):
        return self.participants_delegate

    def get_vital_state(self):
        return self.vital_state

    def get_inventory(self):
        return self.inventory

    def get_available_tool_types(self):
        return self.tool_delegate.get_available_tool_types()

    def _init_tools(self, tool_delegate):
        tool_delegate.add_all_available_tool_types([
            ToolType.USE, ToolType.MOVE_TO, ToolType.INSPECT, 
            ToolType.REST, ToolType.TAKE, ToolType.GIVE,
            ToolType.SPEAK
        ])

    def _init_personality_matrix(self, personality_mat):
        personality_mat.reset_value()

    def _init_relationship_score_matrix(self, relationship_score_mat):
        relationship_score_mat.reset_value()

    def perceive_agents(self):
        all_agents = self.world_system_manager.agent_manager.get_agents()
        detected_agents = self.object_detector.detect_agents(self, all_agents)
        return detected_agents

    def perceive_objects(self):
        world_objects = self.world_system_manager.object_manager.get_objects_by_type(ObjectType.ITEM)
        detected_entities = self.object_detector.detect_objects(self, world_objects)
        return detected_entities
    
    def perform_brain_cleanup(self):
        self.engine.perform_brain_cleanup()

    def set_enable_thinking(self, enable):
        self.enable_thinking = enable