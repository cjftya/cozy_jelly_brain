class WorldType:
    CAST_AWAY_SIM = 0
    NEBULA_TOWER_SIM = 1


class WorldTypeName:
    CAST_AWAY_SIM = "CAST_AWAY_SIM"
    NEBULA_TOWER_SIM = "NEBULA_TOWER_SIM"

    @staticmethod
    def get_name(world_type):
        if world_type == WorldType.CAST_AWAY_SIM:
            return WorldTypeName.CAST_AWAY_SIM
        elif world_type == WorldType.NEBULA_TOWER_SIM:
            return WorldTypeName.NEBULA_TOWER_SIM
        else:
            return "NONE_WORLD"
