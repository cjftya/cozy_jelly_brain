from sim.world.event_trigger import ThinkEventType
from sim.object_meta.object_type import ObjectType
from log import Logger

class DynamicToolExecutor:
    @staticmethod
    def execute(tool, params, agent, world_system_manager):
        Logger.log("Action", f"[{agent.name}] 동적 도구 발동: {tool.name}")
        pass