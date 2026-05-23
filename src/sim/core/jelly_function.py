from log import Logger
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sim.world.world_system_manager import WorldSystemManager
    from sim.agents.agent import Agent
from sim.world.event_trigger import ThinkEventType
from sim.object_meta.object_type import ObjectType, ObjectDetailType

class JellyFunction:
    def __init__(self, world_system_manager: "WorldSystemManager"):
        self.world_system_manager = world_system_manager

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
            self.world_system_manager.log_system_event(f"Action Execution Error: {function_name}, error: function not found")
            return
        
        parameters = action_call.get('parameters', {})
        try:
            self.action_map[function_name](parameters, agent)
        except Exception as e:
            self.world_system_manager.log_system_event(f"Action Execution Error: {function_name}, error: {e}")

    # 1. 이동: move_to(location)
    def _move_to(self, params, agent: "Agent"):
        location = params.get('location', None)
        reason = params.get('reason', None)
        if location and location in agent.location_delegate.get_available_locations():
            # 문자열 상태 정보 업데이트
            agent.location_delegate.set_current_location(location)
            
            # 무한 확장 절대 좌표계를 고려한 로컬 좌표 초기화
            target_space = None
            all_objects = self.world_system_manager.object_manager.get_objects()
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

            self.world_system_manager.log_world_event(f"{agent.name}가 {location} 공간으로 이동.") 
        else:
            self.world_system_manager.log_world_event(f"{agent.name}가 {location} 공간으로 이동할 수 없음.")

    # 2. 사회: speak(agent_name, message)
    def _speak(self, params, agent: "Agent"):
        target_agent_name = params.get('agent_name')
        target_agent = self.world_system_manager.agent_manager.get_agent_by_name(target_agent_name)
        message = params.get('message', '')
        if target_agent:
            target_agent.push_think_event(ThinkEventType.SPEAK, message, agent.name)
            self.world_system_manager.log_world_event(f"{agent.name}가 {target_agent.name}에게 말을 걸었음.")
        else:
            self.world_system_manager.log_world_event(f"{agent.name}가 {target_agent_name}에게 말을 걸 수 없음.")

    # 3. 소유: take(object)
    def _take(self, params, agent: "Agent"):
        object_id = params.get('object_id')
        target_object = self.world_system_manager.object_manager.get_object(object_id)
        if target_object:
            agent.get_inventory().add_object(target_object)
            self.world_system_manager.log_world_event(f"{agent.name}가 {target_object.name}을 획득.")
        else:
            self.world_system_manager.log_world_event(f"{agent.name}가 {object_id}을 획득할 수 없음.")

    # 4. 사회: give(target, object)
    def _give(self, params, agent):
        target_agent_name = params.get('agent_name')
        target_agent = self.world_system_manager.agent_manager.get_agent_by_name(target_agent_name)
        if not target_agent:
            self.world_system_manager.log_system_event("skip function call: give, target agent null")
            return
        
        object_id = params.get('object_id')
        target_object = self.world_system_manager.object_manager.get_object(object_id)
        if not target_object:
            self.world_system_manager.log_system_event("skip function call: give, target object null")
            return
        
        agent.get_inventory().remove_object(target_object)
        target_agent.get_inventory().add_object(target_object)

        context = f"{agent.name}가 나에게 {target_object.name}를 주었음."
        target_agent.push_think_event(ThinkEventType.SPEAK, context, agent.name)
        self.world_system_manager.log_world_event(f"{agent.name}가 {target_agent.name}에게 {target_object.name}을 전달.")

    # 5. 지각: inspect(object)
    def _inspect(self, params, agent):
        reason = params.get('reason', None)
        object_id = params.get('object_id')
        target_object = self.world_system_manager.object_manager.get_object(object_id)
        if not target_object:
            self.world_system_manager.log_system_event("skip function call: inspect, target object null")
            return

        context = f"[{reason}] 라는 이유로, 나는 {target_object.name}를 자세히 관찰함. 관찰한 결과: {target_object.detail}"
        agent.push_think_event(ThinkEventType.INSPECT, context, agent.name)
        self.world_system_manager.log_world_event(f"{agent.name}가 {target_object.name}을 관찰.")

    # 6. 상호작용: use(object)
    def _use(self, params, agent):
        object_id = params.get('object_id')
        target_object = self.world_system_manager.object_manager.get_object(object_id)
        if target_object:
            object_detail_type, is_consumed = target_object.use()
            if is_consumed:
                # 소모품 사용
                if object_detail_type == ObjectDetailType.FOOD or object_detail_type == ObjectDetailType.DRINK:
                    if object_detail_type == ObjectDetailType.FOOD:
                        agent.vital_state.update_hunger(-25)
                    elif object_detail_type == ObjectDetailType.DRINK:
                        agent.vital_state.update_hunger(-5)
                else:
                    # 음식 이외 다른 것들 (감기약 등)
                    pass

                # 소모품 제거 (모든 곳에서 제거)
                agent.get_inventory().remove_object(target_object)
                self.world_system_manager.object_manager.remove_object(target_object)

                self.world_system_manager.log_world_event(f"{agent.name}가 {target_object.name}을 사용.")
            else:
                # 상태 변화가 일어나는 경우
                state, state_detail = target_object.get_current_state()
                if state and state_detail:
                    state_str = f" ({state} 상태로 전환)" if state else ""
                    self.world_system_manager.log_world_event(f"{agent.name}가 {target_object.name}을 사용함. {state_str}")
        else:
            self.world_system_manager.log_world_event(f"{agent.name}가 {object_id}을 사용할 수 없음.")

    # 7. 생존: rest
    def _rest(self, params, agent):
        agent.perform_brain_cleanup()
        agent.vital_state.update_fatigue(-70)
        agent.vital_state.update_health(50)
        self.world_system_manager.log_world_event(f"{agent.name}가 휴식함.")

    # 8. 정지: none
    def _none_action(self, params, agent):
        self.world_system_manager.log_world_event(f"{agent.name}가 행동을 하지 않음.")