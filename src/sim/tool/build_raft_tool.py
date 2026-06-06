from sim.tool.base_tool import BaseTool
from sim.tool.tool_type import ToolType

class BuildRaftTool(BaseTool):
    def __init__(self):
        super().__init__("build_raft", ToolType.BUILD_RAFT)

    def get_description(self):
        return "인벤토리에 탈출을 위한 네 가지 필수 자원('단단한 야자나무 통나무', '질긴 야생 덩굴', '찢어진 난파선 돛천', '부러진 철제 키 조각')이 모두 수집되어 있을 때만 실행 가능함. 목공 작업대에서 자원들을 완벽히 결합하여 거친 바다를 돌파할 탈출용 뗏목을 제작하고 능동적 탈출을 집행함."

    def get_params(self):
        return ''

    def execute(self, params, agent, world_system_manager):
        inv = agent.get_inventory()
        part1 = inv.get_pack("단단한 야자나무 통나무")
        part2 = inv.get_pack("질긴 야생 덩굴")
        part3 = inv.get_pack("찢어진 난파선 돛천")
        part4 = inv.get_pack("부러진 철제 키 조각")
        
        if len(part1) > 0 and len(part2) > 0 and len(part3) > 0 and len(part4) > 0:
            world_system_manager.log_world_event(f"[능동적 운명 개척] {agent.name}가 섬 곳곳의 사선을 넘나들며 수집한 네 개의 핵심 부품(통나무, 덩굴, 돛천, 키 조각)을 목공 작업대에서 완벽하게 결합해 냄. 마침내 험난한 집사광 파도를 가르고 JAIN의 손을 잡은 채 망망대해를 건너 무사히 탈출하는 데 성공함.")
            world_system_manager.log_system_event("CRITICAL_END: SIMULATION_SUCCESS_RAFT_ESCAPE")
            world_system_manager.event_trigger.stop()
        else:
            world_system_manager.log_world_event(f"{agent.name}가 뗏목 조립을 시도했으나, 아직 4개의 필수 탈출 자원 중 일부가 가방에 부족함을 깨닫고 좌절함.")