from sim.tool.base_tool import BaseTool
from sim.tool.tool_type import ToolType
from sim.world.event_trigger import ThinkEventType


class SpeakTool(BaseTool):
    def __init__(self):
        super().__init__("speak", ToolType.SPEAK)

    def get_description(self):
        return "주변 에이전트와 소통함. 대화 목적을 달성했거나 작별 인사를 건네며 대화를 완전히 끝내고 자율 생존 행동으로 복귀하고 싶다면 반드시 finish 값을 true로 선언할 것."

    def get_params(self):
        return '{"agent_name": "Available Participants 중 한명", "message": "대화할 내용", "finish": true/false}'

    def execute(self, params, agent, world_system_manager):
        target_agent_name = params.get("agent_name")
        target_agent = world_system_manager.agent_manager.get_agent_by_name(
            target_agent_name
        )
        message = params.get("message", "")
        finish = bool(params.get("finish", False))
        if target_agent:
            if finish:
                world_system_manager.log_world_event(
                    f"{target_agent.name}와(과)의 대화가 종료되고 {agent.name}는 자율 행동으로 돌아갔습니다."
                )
            else:
                target_agent.push_think_event(ThinkEventType.SPEAK, message, agent.name)
                world_system_manager.log_world_event(
                    f"{agent.name}가 {target_agent.name}에게 말을 걸었음."
                )
        else:
            world_system_manager.log_world_event(
                f"{agent.name}가 {target_agent_name}에게 말을 걸 수 없음."
            )
