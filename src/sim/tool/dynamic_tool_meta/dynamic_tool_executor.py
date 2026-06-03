from sim.world.event_trigger import ThinkEventType
from sim.action.modify_vital_action import ModifyVitalAction
from sim.action.modify_relationship_score_action import ModifyRelationshipScoreAction
from sim.action.modify_mind_action import ModifyMindAction
from sim.agent_meta.vital_state import VitalType
from log import Logger

class DynamicToolExecutor:
    @staticmethod
    def execute(tool, params, agent, world_system_manager):
        skill_type = tool.skill_type
        feedback_messages = []

        # 에이전트 대상 스킬(agent_skill) 원자성 격발 프로세스
        if skill_type == "agent_skill":
            target_name = params.get("applied_target", agent.name)
            target_agent = world_system_manager.agent_manager.get_agent_by_name(target_name)
            
            if not target_agent:
                world_system_manager.log_system_event(f"DynamicToolExecutor Error: 대상 [{target_name}]을 찾을 수 없습니다.")
                return

            # 미디에이터가 사출한 가중치 공식 순회 격발
            for effect in tool.effects:
                meta_tag = effect.get("meta_tag")
                intensity = float(effect.get("intensity", 0.5))

                # A. 생체 신호 변화 집행 (Health 변동 기준값 40.0 배율 정렬)
                if meta_tag == "VITAL_MODIFIER":
                    action = ModifyVitalAction(world_system_manager)
                    vital_impact = 40.0 * intensity
                    action.execute(target_agent.name, VitalType.HEALTH, vital_impact)
                    status_mode = "회복" if intensity > 0 else "데미지"
                    feedback_messages.append(f"{target_agent.name}의 체력 {status_mode} 조절됨")

                # B. 정신 회로 및 호르몬 굴절 집행 (기본값 fear_decisive 공포심 기준 연동)
                elif meta_tag == "MIND_MODIFIER":
                    action = ModifyMindAction(world_system_manager)
                    mind_impact = 0.3 * intensity
                    action.execute(target_agent.name, "fear_decisive", mind_impact)
                    feedback_messages.append(f"{target_agent.name}의 공포/결단 매트릭스 변동")

                # C. 사회적 유대감 밀도 조절 집행 (호감도 가감 기준값 15.0 배율 정렬)
                elif meta_tag == "BOND_MODIFIER":
                    action = ModifyRelationshipScoreAction(world_system_manager)
                    bond_impact = int(15.0 * intensity)
                    action.execute(agent.name, target_agent.name, bond_impact)
                    feedback_messages.append(f"{target_agent.name}와의 관계도 수치 변동")

        # 사물 상태 변형 스킬(object_transform) 피드백 정렬
        elif skill_type == "object_transform":
            # 변형 처리는 이미 skill_tool.py의 인스턴스 레벨 포인터에서 직접 갱신 완료됨
            feedback_messages.append("사물의 속성 테이블에 새로운 변형 상태 레이어가 영구 주입되었습니다.")

        # 에이전트 인지 시스템으로 실시간 실행 피드백 주입 (Working Memory)
        final_feedback = " / ".join(feedback_messages) if feedback_messages else "능력이 세계선에 격발되었으나 수치적 왜곡을 일으키지 않았습니다."
        agent.push_think_event(ThinkEventType.DYNAMIC_TOOL_FEEDBACK, final_feedback)