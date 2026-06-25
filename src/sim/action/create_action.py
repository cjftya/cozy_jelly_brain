from sim.action.base_action import BaseAction
from sim.object_meta.object_type import ObjectType
from sim.objects.building_object import BuildingObject
from sim.objects.item_object import ItemObject
from sim.objects.space_object import SpaceObject


class CreateAction(BaseAction):
    def __init__(self, world_system_manager):
        super().__init__(world_system_manager)

    def execute(self, *args):
        # args: created_name, agent_name, detail
        if len(args) < 3:
            self.world_system_manager.log_system_event(
                "skip function call: create, args insufficient"
            )
            return False

        created_name = args[0]
        agent_name = args[1]
        detail = args[2]

        agent = self.world_system_manager.agent_manager.get_agent_by_name(agent_name)
        if not agent:
            self.world_system_manager.log_system_event(
                "skip function call: create, agent not found"
            )
            return False

        new_obj = ItemObject(name=created_name, detail=detail, parent=agent)

        agent.inventory.add_object(new_obj)
        return True
