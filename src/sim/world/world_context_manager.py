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

class WorldContextManager:
    def __init__(self):
        self.llm_requester = None

        self.agent_manager = AgentManager()
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
        self.refresh_inventory = None
        self.append_agent_chat_log = None
        self.append_world_log = None
        self.refresh_ascii_map = None
        self.append_system_log = None
        
    def start(self, llm_requester, 
            refresh_biometrics=None,
            refresh_inventory=None,
            append_agent_chat_log=None,
            append_world_log=None,
            refresh_ascii_map=None,
            append_system_log=None):
        self.llm_requester = llm_requester
        self.refresh_biometrics = refresh_biometrics
        self.refresh_inventory = refresh_inventory
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

        for agent in self.agents:
            agent.tick(self.time_engine.time_scale)

        details = self.agent_view.update_agent_details_view(self.agents[0])
        self.refresh_biometrics(details)

        event_objects = self.event_trigger.check_triggers(self.agents, self.weather_engine.weather)
        for obj in event_objects:
            event_agent = obj[0]
            event_type = obj[1]
            event_message = obj[2]

            if event_type == EventType.FATIGUE_TRIPPED:
                event_agent.push_think_event(ThinkEventType.FATIGUE, event_message, None)
            
            if event_type == EventType.HUNGER_TRIPPED:
                event_agent.push_think_event(ThinkEventType.HUNGER, event_message, None)

            if event_type == EventType.RANDOM_SCAN:
                for agent in self.agents:
                    agent.scan(event_message)

        for agent in self.agents:
            result = agent.think_tick()
            if result:
                time.sleep(IrisLlmApi.get_loop_delay())

    def get_state_context(self):
        return f"""\
{self.time_engine.get_context()}\n
{self.weather_engine.get_context()}"""


        