from sim.object_meta.object_manager import ObjectManager
from sim.agent_meta.agent_manager import AgentManager
from sim.world.world_object_creator import WorldObjectCreator
from sim.world.weather_engine import WeatherEngine
from sim.world.time_engine import TimeEngine
from sim.sim_agent.lim import Lim
from sim.world.event_trigger import EventTrigger, EventType

class WorldContextManager:
    def __init__(self):
        self.agent_manager = AgentManager()
        self.object_manager = ObjectManager()
        self.world_object_creator = WorldObjectCreator()
        self.weather_engine = WeatherEngine()
        self.time_engine = TimeEngine()
        self.event_trigger = EventTrigger()

        lim = Lim(world_context_manager=self)
        lim.set_enable_thinking(True)
        self.agent_manager.add_agent(lim)
        self.agents = self.agent_manager.get_agents()
        
    def start(self):
        objects = self.world_object_creator.create_lim_world()
        for obj in objects:
            self.object_manager.add_object(obj)

        for agent in self.agents:
            agent.start()

    def stop(self):
        for agent in self.agents:
            agent.stop()

        self.agent_manager.clear_agents()
        self.object_manager.clear_objects()

    def tick(self):
        self.time_engine.tick()
        self.weather_engine.tick(self.time_engine.time_scale, self.time_engine.season)

        for agent in self.agents:
            agent.tick(self.time_engine.time_scale)

        event_objects = self.event_trigger.check_triggers(self.agents, self.weather_engine.weather)
        for obj in event_objects:
            event_agent = obj[0]
            event_type = obj[1]
            event_message = obj[2]

            # TODO: 루프 수정 필요 (순환성 필요)
            # agent 루프에서 event를 주입하는 방향으로 변경 필요
            if event_type == EventType.WEATHER_CHANGE:
                for agent in self.agents:
                    agent.event(event_type, event_message)
            elif event_type == EventType.RANDOM_SCAN:
                for agent in self.agents:
                    agent.search(event_message)

            if event_type == EventType.FATIGUE_TRIPPED or event_type == EventType.HUNGER_TRIPPED:
                event_agent.event(event_type, event_message)

    def get_context(self):
        return f"""\
{self.time_engine.get_context()}\n
{self.weather_engine.get_context()}"""


        