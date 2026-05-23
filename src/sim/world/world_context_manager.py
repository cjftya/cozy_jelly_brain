import time
from sim.iris_llm_api import IrisLlmApi
from sim.object_meta.object_manager import ObjectManager
from sim.agent_meta.agent_manager import AgentManager
from sim.world.world_object_creator import WorldObjectCreator
from sim.world.weather_engine import WeatherEngine
from sim.world.time_engine import TimeEngine
from sim.sim_agent.lim import Lim
from sim.world.event_trigger import EventTrigger, EventType, ThinkEventType
from sim.world.agent_view import AgentView
from sim.world.map_engine import MapEngine

class WorldContextManager:
    def __init__(self):
        self.llm_requester = None

        self.agent_manager = AgentManager()
        self.map_engine = MapEngine(self)
        self.object_manager = ObjectManager()
        self.world_object_creator = WorldObjectCreator()
        self.weather_engine = WeatherEngine()
        self.time_engine = TimeEngine()
        self.event_trigger = EventTrigger()

        lim = Lim(world_context_manager=self)
        self.agent_manager.add_agent(lim)
        self.agents = self.agent_manager.get_agents()

        self.agent_view = AgentView(self)

        self.refresh_biometrics = None
        self.refresh_world_detail = None
        self.append_agent_chat_log = None
        self.append_world_log = None
        self.refresh_ascii_map = None
        self.append_system_log = None
        
    def start(self, llm_requester, 
            refresh_biometrics=None,
            refresh_world_detail=None,
            append_agent_chat_log=None,
            append_world_log=None,
            refresh_ascii_map=None,
            append_system_log=None):
        self.llm_requester = llm_requester
        self.refresh_biometrics = refresh_biometrics
        self.refresh_world_detail = refresh_world_detail
        self.append_agent_chat_log = append_agent_chat_log
        self.append_world_log = append_world_log
        self.refresh_ascii_map = refresh_ascii_map
        self.append_system_log = append_system_log

        # 월드 데이터 초기화
        objects = self.world_object_creator.create_lim_world()
        for obj in objects:
            self.object_manager.add_object(obj)

        for agent in self.agents:
            agent.start(llm_requester)

    def stop(self):
        for agent in self.agents:
            agent.stop()

        self.agent_manager.clear_agents()
        self.object_manager.clear_objects()

    def tick(self):
        time.sleep(1)

        self.time_engine.tick()
        self.weather_engine.tick(self.time_engine.time_scale, self.time_engine.season)

        root_agent = self.agents[0]

        for agent in self.agents:
            agent.tick(self.time_engine.time_scale)

        agent_details = self.agent_view.update_agent_details_view(root_agent)
        self.refresh_biometrics(agent_details)

        world_details = self.agent_view.update_world_details_view()
        self.refresh_world_detail(world_details)

        map_details = self.agent_view.update_ascii_map_view(root_agent)
        self.refresh_ascii_map(map_details)

        event_objects = self.event_trigger.check_triggers(self.agents, self.weather_engine.weather)
        for obj in event_objects:
            event_agent = obj[0]
            event_type = obj[1]
            event_message = obj[2]

            if event_type == EventType.FATIGUE_TRIPPED:
                event_agent.push_think_event(ThinkEventType.FATIGUE, event_message, None)
                self.log_world_event(f"{event_agent.name}가 피로를 느낌.")
            
            if event_type == EventType.HUNGER_TRIPPED:
                event_agent.push_think_event(ThinkEventType.HUNGER, event_message, None)
                self.log_world_event(f"{event_agent.name}가 허기를 느낌.")

            if event_type == EventType.RANDOM_SCAN:
                for agent in self.agents:
                    self.log_world_event(f"{agent.name}가 주변 탐색을 시도 함.")
                    agent.scan(event_message)
            
            if event_type == EventType.RANDOM_MOVE:
                for agent in self.agents:
                    self.log_world_event(f"{agent.name}가 이동을 시도 함.")
                    if not agent.move():
                        self.log_world_event(f"{agent.name}가 이동에 실패 함.")

        for agent in self.agents:
            result = agent.think_tick()
            if result:
                agent_log = self.parse_think_result(result)
                if agent_log:
                    self.log_agent_event(agent_log)
                time.sleep(IrisLlmApi.get_loop_delay())

    def parse_think_result(self, result):
        # 1. 문자열로 들어왔거나 "None" 텍스트인 경우 방어 처리
        if not result or result == "None":
            return None
            
        # 2. 혹시 result가 딕셔너리가 아니라 문자열(JSON) 상태라면 파싱 시도
        if isinstance(result, str):
            try:
                import json
                result = json.loads(result)
            except Exception:
                return f"--- CRITICAL: LOG PARSE ERROR ---\nRaw: {result}"

        # 3. 안전하게 데이터 추출
        subjective_perception = result.get('subjective_perception', '')
        unconscious_impulse = result.get('unconscious_impulse', '')
        internal_strategy = result.get('internal_strategy', '')
        
        action_call = result.get('action_call', {}) or {} # None 방지
        function = action_call.get('function', 'NONE')
        parameters = action_call.get('parameters', {})
        reason = action_call.get('reason', 'No reason provided.')
        
        # 4. 무의식 파편 가로 정렬 뷰 포매팅 (아까 정한 블록 스타일)
        if unconscious_impulse:
            impulses = [imp.strip() for imp in unconscious_impulse.split(',') if imp.strip()]
            unconscious_str = "  ".join([f"▶ [{imp}]" for imp in impulses])
        else:
            unconscious_str = "▶ [NONE]"

        # 5. Graph DB 메모리 파트 예외 방어 및 파싱
        memories_to_save = result.get('memories_to_save', [])
        # 만약 LLM이 텍스트 형태로 중복 직렬화해서 보냈을 경우 2차 방어
        if isinstance(memories_to_save, str):
            try:
                import json
                memories_to_save = json.loads(memories_to_save)
            except Exception:
                memories_to_save = []

        memories_str = ''
        if memories_to_save:
            for memory in memories_to_save:
                try:
                    memories_str += f"\n[RELATION] {memory.get('subject')} ──({memory.get('relation')})──> {memory.get('object')}\n"
                    memories_str += f" └─ [METADATA] {memory.get('metadata', {})}\n"
                except Exception:
                    continue
        else:
            memories_str = "[NO GRAPH MEMORY UPDATE]"

        # 6. 최종 압축 템플릿 출력
        agent_log = f"""
❖ SUBJECTIVE REFRACTION (주관적 환경 왜곡 수용)
"{subjective_perception}"

❖ UNCONSCIOUS IMPULSE (무의식적 욕구 분출)
{unconscious_str}

❖ INTERNAL STRATEGY (단독 행동 및 생존 전략)
{internal_strategy}

❖ SYSTEM ACTION EXECUTION (최종 의사결정 집행)
• FUNCTION : {str(function).upper()}
• PARAMS   : {parameters}
• REASON   : {reason}

❖ KUZU GRAPH MEMORY UPDATE (시냅스 기억 저장 로그)
{memories_str.strip()}


----------------------------------------------------------------------
"""

        return agent_log

    def log_world_event(self, log):
        self.append_world_log(f"[{self.time_engine.get_date()} {self.time_engine.get_clock()}] {log}")

    def log_system_event(self, log):
        self.append_system_log(f"[{self.time_engine.get_date()} {self.time_engine.get_clock()}] {log}")

    def log_agent_event(self, log):
        self.append_agent_chat_log(f"[{self.time_engine.get_date()} {self.time_engine.get_clock()}]\n{log}")

    def get_state_context(self):
        return f"""\
{self.time_engine.get_context()}\n
{self.weather_engine.get_context()}"""


        