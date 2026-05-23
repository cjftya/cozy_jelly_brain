import time
from sim.core.jelly_llm_api import JellyLlmApi
from sim.util.object_manager import ObjectManager
from sim.util.agent_manager import AgentManager
from sim.agents.lim import Lim
from sim.world.event_trigger import EventTrigger, EventType, ThinkEventType
from sim.world.world_view_manager import WorldViewManager
from sim.world.map_engine import MapEngine
from sim.world.world_object_creator import WorldObjectCreator
from sim.world.weather_engine import WeatherEngine
from sim.world.time_engine import TimeEngine
from log import Logger

class WorldSystemManager:
    def __init__(self):
        self.llm_requester = None

        # 관리자
        self.agent_manager = AgentManager()
        self.object_manager = ObjectManager()

        # 엔진
        self.world_object_creator = WorldObjectCreator()
        self.weather_engine = WeatherEngine()
        self.time_engine = TimeEngine()
        self.event_trigger = EventTrigger()
        self.map_engine = MapEngine(self)
        self.world_view_manager = WorldViewManager(self)

        lim = Lim(world_system_manager=self)
        self.agent_manager.add_agent(lim)
        self.agents = self.agent_manager.get_agents()

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

        agent_details = self.world_view_manager.update_agent_details_view(root_agent)
        self.refresh_biometrics(agent_details)

        world_details = self.world_view_manager.update_world_details_view()
        self.refresh_world_detail(world_details)

        map_details = self.world_view_manager.update_ascii_map_view(root_agent)
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
                agent_log = self.world_view_manager.update_agent_log_view(agent, result)
                self.log_agent_event(agent_log)
                time.sleep(JellyLlmApi.get_loop_delay())

    def log_world_event(self, log):
        self.append_world_log(f"[{self.time_engine.get_date()} {self.time_engine.get_clock()}] {log}")

    def log_system_event(self, log):
        self.append_system_log(f"[{self.time_engine.get_date()} {self.time_engine.get_clock()}] {log}")
        Logger.log("[SYSTEM]", log)

    def log_agent_event(self, log):
        self.append_agent_chat_log(f"[{self.time_engine.get_date()} {self.time_engine.get_clock()}]\n{log}")

    def get_state_context(self):
        return f"""\
{self.time_engine.get_context()}\n
{self.weather_engine.get_context()}"""


        