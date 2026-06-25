from sim.tool.base_tool import BaseTool
from sim.tool.tool_type import ToolType


class BuildRaftTool(BaseTool):
    def __init__(self):
        super().__init__("build_raft", ToolType.BUILD_RAFT)

    def get_description(self):
        return "[조건: 인벤토리에 '단단한 야자나무 통나무', '질긴 야생 덩굴', '찢어진 난파선 돛천', '부러진 철제 키 조각' 4개 자원 필수] 목공 작업대에서 자원을 결합하여 탈출용 뗏목을 제작하고 섬을 즉시 탈출함(시뮬레이션 성공 엔딩)."

    def get_params(self):
        return ""

    def execute(self, params, agent, world_system_manager):
        inv = agent.inventory
        part1 = inv.get_objects_by_name("단단한 야자나무 통나무")
        part2 = inv.get_objects_by_name("질긴 야생 덩굴")
        part3 = inv.get_objects_by_name("찢어진 난파선 돛천")
        part4 = inv.get_objects_by_name("부러진 철제 키 조각")

        if len(part1) > 0 and len(part2) > 0 and len(part3) > 0 and len(part4) > 0:
            world_system_manager.log_world_event(
                f"[능동적 운명 개척] {agent.name}가 섬 곳곳의 사선을 넘나들며 수집한 네 개의 핵심 부품(통나무, 덩굴, 돛천, 키 조각)을 목공 작업대에서 완벽하게 결합해 냄. 마침내 험난한 집사광 파도를 가르고 JAIN의 손을 잡은 채 망망대해를 건너 무사히 탈출하는 데 성공함."
            )
            world_system_manager.log_system_event(
                "CRITICAL_END: SIMULATION_SUCCESS_RAFT_ESCAPE"
            )
            world_system_manager.event_trigger.stop()
        else:
            world_system_manager.log_world_event(
                f"{agent.name}가 뗏목 조립을 시도했으나, 아직 4개의 필수 탈출 자원 중 일부가 가방에 부족함을 깨닫고 좌절함."
            )
