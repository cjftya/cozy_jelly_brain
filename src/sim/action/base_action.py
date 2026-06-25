class BaseAction:
    def __init__(self, world_system_manager):
        self.world_system_manager = world_system_manager

    def execute(self, *args) -> bool:
        return True
