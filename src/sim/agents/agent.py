import random
from sim.core.jelly_engine import JellyEngine
from sim.agent_meta.participants_delegate import ParticipantsDelegate
from sim.agent_meta.location_delegate import LocationDelegate
from sim.agent_meta.tool_detegate import ToolDelegate
from sim.agent_meta.vital_state import VitalState
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

class Agent:
    def __init__(self, name="UNKNOWN", identifier="UNKNOWN", world_system_manager: "WorldSystemManager"=None):
        self.id = GlobalUtil.gen_agent_id()
        self.name = name
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
        self.engine = JellyEngine(self.name, self.world_system_manager)

        # 생체 정보
        self.vital_state = VitalState()

        # 주변 에이전트 정보
        self.participants_delegate = ParticipantsDelegate()

        # 공간 정보
        self.location_delegate = LocationDelegate()

        # 대화 모드 툴 정보
        self.dia_tool_delegate = ToolDelegate()

        # 탐색 모드 툴 정보
        self.exp_tool_delegate = ToolDelegate()

        # 인벤토리
        self.inventory = ObjectManager()

        # 좌표
        self.position = Point()
        
        # 시야 감지 엔진
        self.object_detector = ObjectDetector()

        # 성격 매트릭스 (0 ~ 1.0)
        # logic_emotion : 감성적인가 이성적인가
        # defensive_open : 방어적인가 개방적인가
        # fear_decisive : 공포에 우유부단한가 용감하고 단호한가
        # obedient_rebellious : 복종적인가 반항적인가
        # curiosity_indifference : 호기심이 많은가 무관심한가
        self.personality_matrix = self.get_personality_matrix()

        # 환경적 요인으로 인한 누적 변동치 (-0.15 ~ +0.15) 외부에서 사용되지않고 내부에서만 연동
        self.env_deltas = {
            'logic_emotion': 0.0,
            'defensive_open': 0.0,
            'fear_decisive': 0.0,
            'curiosity_indifference': 0.0,
            'obedient_rebellious': 0.0
        }

        # 관계 정보
        self.relationship_map = {}

        self._create_tools(self.dia_tool_delegate, self.exp_tool_delegate)

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
            res = self.engine.think_event_normal(agent=self, event_type=None, external_event=combined_signal, available_tool_types=self.get_available_tool_types(False))
            return res

        # find agent signal
        if ThinkEventType.FIND_AGENT in self.think_event_queue.keys():
            think_event = self.think_event_queue[ThinkEventType.FIND_AGENT]
            think_event_message = think_event.get("message", "")
            found_agents = think_event.get("data", None)

            self.think_event_queue.clear()
            res = self.engine.think_event_speak(user_input=think_event_message, agent=self, available_agents=found_agents, from_scan=True, available_tool_types=self.get_available_tool_types(True))
            return res

        # find item signal
        if ThinkEventType.FIND_ITEM in self.think_event_queue.keys():
            think_event = self.think_event_queue[ThinkEventType.FIND_ITEM]
            think_event_message = think_event.get("message", "")
            found_objects = think_event.get("data", None)

            self.think_event_queue.clear()
            res = self.engine.think_event_detect_objects(agent=self, external_event=think_event_message, detected_objects=found_objects, available_tool_types=self.get_available_tool_types(False))
            return res
        
        # speak signal
        if ThinkEventType.SPEAK in self.think_event_queue.keys():
            think_event = self.think_event_queue[ThinkEventType.SPEAK]
            think_event_message = think_event.get("message", "")
            found_agent_name = think_event.get("data", None)
            user_input = f"[From {found_agent_name}] : {think_event_message}"
            available_agent = self.world_system_manager.agent_manager.get_agent_by_name(found_agent_name)

            self.think_event_queue.clear()
            res = self.engine.think_event_speak(user_input=user_input, agent=self, available_agents=[available_agent], from_scan=False, available_tool_types=self.get_available_tool_types(True))
            return res

        # event signal
        combined_signal = ""
        for think_event_type, think_event in self.think_event_queue.items():
            think_event_message = think_event.get("message", "")
            combined_signal += f"{think_event_message}\n"
        self.think_event_queue.clear()
        res = self.engine.think_event_normal(agent=self, event_type=None, external_event=combined_signal, available_tool_types=self.get_available_tool_types(False))
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

        # 40센트 확률로 대화 60퍼센트 확률로 사물탐색
        if random.random() < 0.4:
            if len(found_agents) > 0 and self.vital_state.fatigue < 70 and self.vital_state.health > 30:
                ran_num = self.personality_matrix['defensive_open'] + random.random()
                if ran_num >= 1.0:
                    msg = " 주변에 다른 상대가 보인다. 너의 신체적 겹핍, 목적 달성에 따라 대상에게 말을 걸지 무시할지 판단하라. 대화가 의미 없다면 'move_to' 도구를 이용하여 장소를 이동하라."
                    self.push_think_event(ThinkEventType.FIND_AGENT, external_event + msg, found_agents)
                    return

        if random.random() < 0.6:
            if len(found_objects) > 0:
                msg = " 주위에 관심있는 사물이 있다. 너의 신체적 겹핍, 목적 달성에 따라 사물을 조사하거나 획득할지 결정하라."
                self.push_think_event(ThinkEventType.FIND_ITEM, external_event + msg, found_objects)
                return

    def _update_environmental_debuff(self, time_scale, day_cycle, weather_type):
        MAX_ENV_LIMIT = 0.15

        def apply_env_change(key, change_val):
            current_env_delta = self.env_deltas.get(key, 0.0)
            new_env_delta = current_env_delta + change_val
            
            # 환경으로 인한 누적 변화량이 상대적 한계선(±0.15) 내에 있을 때만 실행
            if -MAX_ENV_LIMIT <= new_env_delta <= MAX_ENV_LIMIT:
                self.env_deltas[key] = round(new_env_delta, 3)
                if key in self.personality_matrix:
                    new_matrix_val = self.personality_matrix[key] + change_val
                    self.personality_matrix[key] = max(0.0, min(1.0, round(new_matrix_val, 3)))

        # 시간대별 공통 굴절 (밤/저녁 ➔ 정서 하락 유도)
        if day_cycle == DayCycleType.NIGHT:
            apply_env_change('fear_decisive', -(0.1 * time_scale))
            apply_env_change('logic_emotion', -(0.1 * time_scale))
        elif day_cycle == DayCycleType.EVENING:
            apply_env_change('fear_decisive', -(0.05 * time_scale))
            
        # 기후별 공통 굴절 (악천후 디버프 vs 맑은 날 버프)
        if weather_type in [WeatherType.RAINY, WeatherType.CLOUDY]:
            apply_env_change('logic_emotion', -(0.1 * time_scale))
            apply_env_change('curiosity_indifference', +(0.05 * time_scale)) # 무관심 소폭 증가
            
        elif weather_type in [WeatherType.THUNDERSTORM]:
            apply_env_change('defensive_open', -(0.2 * time_scale))  # 방어성 증가
            apply_env_change('fear_decisive', -(0.2 * time_scale))   # 공포성 증가
            
        elif weather_type == WeatherType.CLEAR:
            # 맑은 날씨에는 최대 상한선(+0.15)을 넘지 않는 선에서 이성과 개방성을 기분 좋게 부스팅
            apply_env_change('logic_emotion', +(0.05 * time_scale))
            apply_env_change('defensive_open', +(0.05 * time_scale))

    def set_serper_api_key(self, api_key):
        if self.engine:
            self.engine.set_serper_api_key(api_key)

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

        # 중괄호{} 내부에 이름: 점수 형태로 인라인 조인
        pairs = [f"{name}: {score}" for name, score in self.relationship_map.items()]
        return f"{{{', '.join(pairs)}}}"

    def get_location_delegate(self):
        return self.location_delegate

    def get_participant_delegate(self):
        return self.participants_delegate

    def get_vital_state(self):
        return self.vital_state

    def get_inventory(self):
        return self.inventory

    def get_available_tool_types(self, is_dialogue_mode):
        if is_dialogue_mode:
            return self.dia_tool_delegate.get_available_tool_types()
        else:
            return self.exp_tool_delegate.get_available_tool_types()

    def _create_tools(self, dia_tool_delegate, exp_tool_delegate):
        dia_tool_delegate.add_all_available_tool_types(
            [ToolType.SPEAK, ToolType.GIVE, ToolType.NONE]
        )
        
        exp_tool_delegate.add_all_available_tool_types(
            [ToolType.TAKE, ToolType.MOVE_TO, ToolType.INSPECT, ToolType.USE, ToolType.REST, ToolType.NONE]
        )

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