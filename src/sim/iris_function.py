from log import Logger
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sim.world.world_context_manager import WorldContextManager
    from sim.agent import Agent
from sim.world.event_trigger import ThinkEventType
from sim.object_meta.object_type import ObjectType, ObjectDetailType

class IrisFunction:
    def __init__(self, world_context_manager: "WorldContextManager"):
        self.world_context_manager = world_context_manager

        # action map
        self.action_map = {
            "move_to": self._move_to,
            "speak": self._speak,
            "take": self._take,
            "give": self._give,
            "inspect": self._inspect,
            "use": self._use,
            "rest": self._rest,
            "none": self._none_action
        }

    def process_action_call(self, action_call, agent: "Agent"):
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
    def _move_to(self, params, agent: "Agent"):
        location = params.get('location', None)
        reason = params.get('reason', None)
        if location and location in agent.location_delegate.get_available_locations():
            # 문자열 상태 정보 업데이트
            agent.location_delegate.set_current_location(location)
            
            # 무한 확장 절대 좌표계를 고려한 로컬 좌표 초기화
            target_space = None
            all_objects = self.world_context_manager.object_manager.get_objects()
            for obj in all_objects:
                # obj.type == 0 (SpaceObject) 이고 이름이 같은 공간 객체 검색
                if obj.type == ObjectType.SPACE and obj.name == location: 
                    target_space = obj
                    break
            
            # 방의 규격(size) 정보를 찾았다면 정중앙 로컬 좌표계로 자동 세팅
            if target_space and hasattr(target_space, 'size'):
                agent.position.x = float(target_space.size.x // 2)
                agent.position.y = float(target_space.size.y // 2)
            else:
                # 방 오브젝트 누락 예외를 대비한 기본 방어 좌표
                agent.position.x = 4.0
                agent.position.y = 4.0

            self.world_context_manager.log_world_event(f"{agent.name}가 {location} 공간으로 이동.") 
        else:
            self.world_context_manager.log_world_event(f"{agent.name}가 {location} 공간으로 이동할 수 없음.")

    # 2. 사회: speak(agent_name, message)
    def _speak(self, params, agent: "Agent"):
        target_agent_name = params.get('agent_name')
        target_agent = self.world_context_manager.agent_manager.get_agent_by_name(target_agent_name)
        message = params.get('message', '')
        if target_agent:
            target_agent.push_think_event(ThinkEventType.SPEAK, message, agent.name)
            self.world_context_manager.log_world_event(f"{agent.name}가 {target_agent.name}에게 {message}라고 말함.")
        else:
            self.world_context_manager.log_world_event(f"{agent.name}가 {target_agent_name}에게 말을 걸 수 없음.")

    # 3. 소유: take(object)
    def _take(self, params, agent: "Agent"):
        object_id = params.get('object_id')
        target_object = self.world_context_manager.object_manager.get_object(object_id)
        if target_object:
            agent.get_inventory().add_object(target_object)
            self.world_context_manager.log_world_event(f"{agent.name}가 {target_object.name}을 획득.")
        else:
            self.world_context_manager.log_world_event(f"{agent.name}가 {object_id}을 획득할 수 없음.")

    # 4. 사회: give(target, object)
    def _give(self, params, agent):
        target_agent_name = params.get('agent_name')
        target_agent = self.world_context_manager.agent_manager.get_agent_by_name(target_agent_name)
        if not target_agent:
            Logger.log_debug("skip function call: give")
            return
        
        object_id = params.get('object_id')
        target_object = self.world_context_manager.object_manager.get_object(object_id)
        if not target_object:
            Logger.log_debug("skip function call: give")
            return
        
        agent.get_inventory().remove_object(target_object)
        target_agent.get_inventory().add_object(target_object)

        context = f"{agent.name}가 나에게 {target_object.name}를 주었음."
        target_agent.push_think_event(ThinkEventType.SPEAK, context, agent.name)
        self.world_context_manager.log_world_event(f"{agent.name}가 {target_agent.name}에게 {target_object.name}을 전달.")

    # 5. 지각: inspect(object)
    def _inspect(self, params, agent):
        reason = params.get('reason', None)
        object_id = params.get('object_id')
        target_object = self.world_context_manager.object_manager.get_object(object_id)
        if not target_object:
            Logger.log_debug("skip function call: inspect")
            return

        context = f"[{reason}] 라는 이유로, 나는 {target_object.name}를 자세히 관찰함. 관찰한 결과: {target_object.detail}"
        agent.push_think_event(ThinkEventType.INSPECT, context, agent.name)
        self.world_context_manager.log_world_event(f"{agent.name}가 {target_object.name}을 관찰.")

    # 6. 상호작용: use(object)
    def _use(self, params, agent):
        object_id = params.get('object_id')
        target_object = self.world_context_manager.object_manager.get_object(object_id)
        if target_object:
            agent.get_inventory().remove_object(target_object)
            object_detail_type, action = target_object.use()
            if action:
                if object_detail_type == ObjectDetailType.FOOD:
                    agent.vital_state.update_hunger(25)
                elif object_detail_type == ObjectDetailType.DRINK:
                    agent.vital_state.update_hunger(5)
                    
                self.world_context_manager.log_world_event(f"{agent.name}가 {target_object.name}을 사용.")
        else:
            self.world_context_manager.log_world_event(f"{agent.name}가 {object_id}을 사용할 수 없음.")

    # 7. 생존: rest
    def _rest(self, params, agent):
        agent.perform_brain_cleanup()
        agent.vital_state.update_fatigue(-70)
        agent.vital_state.update_health(50)
        self.world_context_manager.log_world_event(f"{agent.name}가 휴식함.")

    # 8. 정지: none
    def _none_action(self, params, agent):
        self.world_context_manager.log_world_event(f"{agent.name}가 행동을 하지 않음.")