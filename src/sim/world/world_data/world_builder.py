import os
from sim.world.weather_engine import WeatherEngine, WeatherType
from sim.world.time_engine import TimeEngine
from sim.world.world_data.world_type import WorldTypeName

class WorldBuilder:
    def __init__(self, world_type):
        self._world_type = world_type
        self._agents = []
        self._objects = []

        self._world_prefix = f"[{WorldTypeName.get_name(world_type)}]"
        self._world_root_path = f"../assets/world_assets"
        self._world_assets_path = f"{self._world_root_path}/{self._world_prefix}"
        self._world_agents_brain_db_path = f"{self._world_assets_path}/agents_brain_db"
        
        if not os.path.exists(self._world_root_path):
            os.makedirs(self._world_root_path)
        if not os.path.exists(self._world_assets_path):
            os.makedirs(self._world_assets_path)
        if not os.path.exists(self._world_agents_brain_db_path):
            os.makedirs(self._world_agents_brain_db_path)

    def _add_agent(self, agent):
        self._agents.append(agent)

    def _add_object(self, obj):
        self._objects.append(obj)

    def get_world_type(self):
        return self._world_type

    def _create_agents(self, world_system_manager):
        pass

    def _create_objects(self, world_system_manager):
        pass

    def _create_weather_engine(self):
        return WeatherEngine()

    def _create_time_engine(self):
        return TimeEngine()

    def _create_world_role(self):
        return ""

    def build(self, world_system_manager):
        time_engine = self._create_time_engine()
        weather_engine = self._create_weather_engine()
        self._create_agents(world_system_manager)
        self._create_objects(world_system_manager)
        world_role = self._create_world_role()
        return [self._agents, self._objects, time_engine, weather_engine, self._world_assets_path, self._world_agents_brain_db_path, world_role]

    