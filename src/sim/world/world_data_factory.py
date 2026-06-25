from sim.world.world_data.castway_world_builder import CastAwayWorldBuilder
from sim.world.world_data.nebula_tower_world_builder import NebulaTowerWorldBuilder
from sim.world.world_data.world_type import WorldType


class WorldDataFactory:
    def __init__(self):
        pass

    def get_world_data(self, world_type, world_system_manager) -> list:
        if world_type == WorldType.CAST_AWAY_SIM:
            return CastAwayWorldBuilder().build(world_system_manager)
        elif world_type == WorldType.NEBULA_TOWER_SIM:
            return NebulaTowerWorldBuilder().build(world_system_manager)

        return [None] * 7
