from sim.world.event_trigger import ThinkEventType
from sim.action.modify_vital_action import ModifyVitalAction
from sim.action.modify_relationship_score_action import ModifyRelationshipScoreAction
from sim.action.take_action import TakeAction
from sim.action.give_action import GiveAction
from sim.action.use_action import UseAction
from sim.action.remove_action import RemoveAction
from sim.action.create_action import CreateAction
from sim.action.modify_mind_action import ModifyMindAction
from sim.agent_meta.vital_state import VitalType
from log import Logger

class DynamicToolExecutor:
    @staticmethod
    def execute(tool, params, agent, world_system_manager):
        world_system_manager.log_world_event(f"[{tool.name}] {agent.name}: {tool.description}")

        success_count = 0
        feedback_messages = []

        # 1. 적용 대상(applied_target) 객체 파악
        applied_target_name = params.get("applied_target")
        applied_agent = world_system_manager.agent_manager.get_agent_by_name(applied_target_name) if applied_target_name else agent

        # 2. 쪼개진 N개의 효과(태그) 순회
        for effect in tool.effects:
            meta_tag = effect.get("meta_tag")
            consumed_objects = effect.get("consumed_objects", []) # 배열 형태로 받음
            intensity = float(effect.get("intensity", 0.5))
            
            try:
                # -------------------------------------------------------------
                # [법칙 1] 생체 수치 조작
                # -------------------------------------------------------------
                if meta_tag == "VITAL_MODIFIER":
                    action = ModifyVitalAction(world_system_manager)
                    impact = 40.0 * intensity
                    
                    action.execute(applied_agent.name, VitalType.HEALTH, impact)
                    
                    action_desc = "회복시킴" if intensity > 0 else "타격을 입힘"
                    feedback_messages.append(f"{applied_agent.name}의 생체 수치를 {action_desc}.")

                # -------------------------------------------------------------
                # [법칙 2] 정신 매트릭스 굴절
                # -------------------------------------------------------------
                elif meta_tag == "MIND_MODIFIER" and applied_agent:
                    action = ModifyMindAction(world_system_manager)
                    key = "fear_decisive"
                    action.execute(applied_agent.name, key, 0.3 * intensity)
                    feedback_messages.append(f"{applied_agent.name}의 심리 매트릭스에 영향을 줌.")

                # -------------------------------------------------------------
                # [법칙 3] 관계도(호감/신뢰) 변동
                # -------------------------------------------------------------
                elif meta_tag == "BOND_MODIFIER" and applied_agent:
                    action = ModifyRelationshipScoreAction(world_system_manager)
                    impact = 10.0 * intensity
                    action.execute(agent.name, applied_agent.name, impact)
                    feedback_messages.append(f"{applied_agent.name}와의 관계가 변함.")

                # -------------------------------------------------------------
                # [법칙 4] 소유권 이전 (TAKE or GIVE)
                # -------------------------------------------------------------
                elif meta_tag == "PROPERTY_TRANSFER":
                    for consumed in consumed_objects:
                        obj_id = consumed.get("object_id")
                        if applied_agent.id == agent.id:
                            action = TakeAction(world_system_manager)
                            action.execute(agent.name, obj_id)
                            feedback_messages.append(f"사물({obj_id})을 획득함.")
                        else:
                            action = GiveAction(world_system_manager)
                            action.execute(applied_agent.name, agent.name, obj_id)
                            feedback_messages.append(f"사물({obj_id})을 {applied_agent.name}에게 건넴.")

                # -------------------------------------------------------------
                # [법칙 5] 아이템 소비/사용
                # -------------------------------------------------------------
                elif meta_tag == "ITEM_CONSUME":
                    for consumed in consumed_objects:
                        obj_id = consumed.get("object_id")
                        count = int(consumed.get("consumed_count", 1))
                        target_object = self._get_object_by_id(world_system_manager, agent, obj_id)
                        
                        if not target_object:
                            continue

                        for _ in range(count):
                            action = UseAction(world_system_manager)
                            action.execute(agent.name, obj_id)
                        
                        feedback_messages.append(f"사물({target_object.name}) {count}개를 사용함.")

                success_count += 1
                
            except Exception as e:
                world_system_manager.log_system_event(f"skip function call: dynamic_tool_executor, error: {e}")
                continue

        # 3. 최종 피드백 루프 (에이전트 인지 기관으로 결과 전송)
        if success_count == 0:
            final_feedback = f"'{tool.name}'을 시도했으나 아무런 변화도 일으키지 못했음."
        else:
            final_feedback = f"'{tool.name}' 시도. " + " / ".join(feedback_messages)
            
        agent.push_think_event(ThinkEventType.DYNAMIC_TOOL_FEEDBACK, final_feedback)

    def _get_object_by_id(self, world_system_manager, agent, id):
        target_object = world_system_manager.object_manager.get_object_by_id(id)
        if target_object:
            return target_object
        else:
            target_inventory_object = agent.inventory.get_object_by_id(id)
            if target_inventory_object:
                return target_inventory_object
            else:
                return None

        