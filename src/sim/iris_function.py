from log import Logger
from sim.world.world_context_manager import WorldContextManager
from sim.agent import Agent

class IrisFunction:
    def __init__(self, world_context_manager: WorldContextManager):
        self._world_context_manager = world_context_manager

        # action map
        self.action_map = {
            "move_to": self._move_to,
            "speak": self._speak,
            "take": self._take,
            "give": self._give,
            "search": self._search,
            "use": self._use,
            "rest": self._rest,
            "none": self._none_action
        }

    def process_action_call(self, action_call, agent: Agent):
        function_name = action_call.get('function')
        if function_name not in self.action_map:
            Logger.log_debug(f"skip function call: {function_name}")
            return
        
        parameters = action_call.get('parameters', {})
        try:
            self.action_map[function_name](parameters, agent)
        except Exception as e:
            Logger.log_debug(f"Action Execution Error ({function_name})", e)

    # 1. 이동: move_to(location)
    def _move_to(self, params, agent: Agent):
        location = params.get('location', None)
        reason = params.get('reason', None)
        if location and location in agent.location_delegate.get_available_locations():
            agent.location_delegate.set_current_location(location)
            agent.location_delegate.set_reason_of_change_location(reason)
        else:
            Logger.log_debug(f"skip function call: move_to, location: {location}")

    # 2. 사회: speak(agent_name, message)
    def _speak(self, params, agent: Agent):
        target_agent_name = params.get('agent_name', 'ALL')
        message = params.get('message', '')
        Logger.log_debug("speak", f"target agent {target_agent_name} is not found")

    # 3. 소유: take(object)
    def _take(self, params, agent: Agent):
        object_id = params.get('object_id')
        Logger.log_debug("Inventory", f"{object_id} 획득 시도")

    # 4. 사회: give(target, object)
    def _give(self, params, agent):
        #todo: 구현필요
        target_agent_id = params.get('agent_id')
        object_id = params.get('object_id')
        Logger.log_debug("Social", f"{target_agent_id}에게 {object_id} 전달")

    # 5. 지각: search(object)
    def _search(self, params, agent):
        #todo: 구현필요
        object_id = params.get('object_id')
        Logger.log_debug("Perception", f"{object_id} 정밀 탐색 수행")

    # 6. 상호작용: use(object)
    def _use(self, params, agent):
        #todo: 구현필요
        object_id = params.get('object_id')
        Logger.log_debug("Interaction", f"{object_id} 사용")

    # 7. 생존: rest
    def _rest(self, params, agent):
        #todo: 구현필요
        Logger.log_debug("Survival", "휴식 및 인지 정리 루틴 시작")
        if hasattr(agent.iris_engine, 'iris_memory'):
            agent.iris_engine.iris_memory.perform_brain_cleanup()

    # 8. 정지: none
    def _none_action(self, params, agent):
        #todo: 구현필요
        pass