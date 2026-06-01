from sim.action.base_action import BaseAction

class CreateAction(BaseAction):
    def __init__(self, world_system_manager):
        super().__init__(world_system_manager)

    def execute(self, *args):
        # args: object_id, x, y
        pass