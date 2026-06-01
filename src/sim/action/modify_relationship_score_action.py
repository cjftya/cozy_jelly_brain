from sim.action.base_action import BaseAction

class ModifyRelationshipScoreAction(BaseAction):
    def __init__(self, world_system_manager):
        super().__init__(world_system_manager)

    def execute(self, *args):
        # args: agent_name, target_agent_name, score

        agent = self.world_system_manager.agent_manager.get_agent_by_name(args[0])
        target_agent = self.world_system_manager.agent_manager.get_agent_by_name(args[1])
        score = int(args[2])

        if not agent or not target_agent:
            self.world_system_manager.log_system_event("skip function call: modify_relationship_score_action, agent or target_agent null")
            return

        agent.get_relationships().add_value(target_agent.name, score)
        