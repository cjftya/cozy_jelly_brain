from sim.world.event_trigger import ThinkEventType
from sim.action.modify_vital_action import ModifyVitalAction
from sim.action.modify_relationship_score_action import ModifyRelationshipScoreAction
from sim.action.modify_mind_action import ModifyMindAction
from sim.agent_meta.vital_state import VitalType
from log import Logger

class DynamicToolExecutor:
    @staticmethod
    def execute(tool, params, agent, world_system_manager):
        pass