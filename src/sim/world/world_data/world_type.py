class WorldType:
    CAST_AWAY_SIM = 0

class WorldTypeName:
    CAST_AWAY_SIM = "CAST_AWAY_SIM"
    
    @staticmethod
    def get_name(world_type):
        if world_type == WorldType.CAST_AWAY_SIM:
            return WorldTypeName.CAST_AWAY_SIM
        else:
            return "NONE_WORLD"

    
    