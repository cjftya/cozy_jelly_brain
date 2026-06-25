from sim.action.base_action import BaseAction


class ModifyRelationshipScoreAction(BaseAction):
    def __init__(self, world_system_manager):
        super().__init__(world_system_manager)

    def execute(self, *args):
        # args: agent_name, target_agent_name, score
        if len(args) != 3:
            self.world_system_manager.log_system_event(
                "skip function call: modify_relationship_score, args length not 3"
            )
            return False

        try:
            agent = self.world_system_manager.agent_manager.get_agent_by_name(args[0])
            target_agent = self.world_system_manager.agent_manager.get_agent_by_name(
                args[1]
            )
            score = int(args[2])

            if not agent or not target_agent:
                self.world_system_manager.log_system_event(
                    "skip function call: modify_relationship_score_action, agent or target_agent null"
                )
                return False

            agent.relationships.add_value(target_agent.name, score)
            self.world_system_manager.log_world_event(
                f"{agent.name} -> {target_agent.name} 호감도 변동: {score}"
            )
            return True
        except Exception as e:
            self.world_system_manager.log_system_event(
                f"skip function call: modify_relationship_score, error: {e}"
            )
            return False
