import time
import random
from sim.core.jelly_llm_api import JellyLlmApi
from sim.util.object_manager import ObjectManager
from sim.util.agent_manager import AgentManager
from sim.util.tool_manager import ToolManager
from sim.world.event_trigger import EventTrigger, EventType, ThinkEventType
from sim.world.world_view_manager import WorldViewManager
from sim.world.map_engine import MapEngine
from sim.world.world_data_factory import WorldDataFactory
from sim.world.world_data.world_type import WorldType
from sim.world.world_mediator import WorldMediator
from sim.core.event_bus import EventBus, EventType as UIEventType
from sim.core.cognitive_worker import CognitiveWorker
from log import Logger

class WorldSystemManager:
    def __init__(self):
        self.llm_requester = None

        self.serper_api_key = None

        # 관리자
        self.agent_manager = AgentManager()
        self.object_manager = ObjectManager()

        # 엔진
        self.weather_engine = None
        self.time_engine = None
        self.event_trigger = EventTrigger()
        self.map_engine = MapEngine(self)
        self.world_view_manager = WorldViewManager(self)
        self.world_data_factory = WorldDataFactory()
        self.tool_manager = ToolManager()
        self.world_mediator = WorldMediator()

        self.world_agents = []
        self.cognitive_worker = None

    def start(self, llm_requester):
        self.llm_requester = llm_requester

        # 월드 데이터 초기화
        world_data = self.world_data_factory.get_world_data(WorldType.NEBULA_TOWER_SIM, self)
        self.world_agents = world_data[0]
        objects = world_data[1]
        self.time_engine = world_data[2]
        self.weather_engine = world_data[3]
        self.world_assets_path = world_data[4]
        self.world_agents_brain_db_path = world_data[5]
        self.world_role = world_data[6]

        # 월드 에이전트 초기화
        for agent in self.world_agents:
            self.agent_manager.add_agent(agent)
            agent.start(self.llm_requester)

        # 월드 오브젝트 초기화
        for obj in objects:
            self.object_manager.add_object(obj)

        # 월드 미디에이터 초기화
        self.world_mediator.start(self.llm_requester, self.world_role)

        # 인지 작업 워커 시작
        self.cognitive_worker = CognitiveWorker(self)
        self.cognitive_worker.start()

        # 에이전트 간 초기 겹침 해소
        self.resolve_agent_overlaps()

    def stop(self):
        if self.cognitive_worker:
            self.cognitive_worker.stop()
            self.cognitive_worker = None

        for agent in self.world_agents:
            agent.stop()

        self.agent_manager.clear_agents()
        self.object_manager.clear_objects()

    def tick(self):
        time.sleep(1)

        # 시간 및 날씨 업데이트
        self.time_engine.tick()
        self.weather_engine.tick(self.time_engine.time_scale, self.time_engine.season)

        # 포커스 에이전트
        focused_agent = self.world_agents[0]

        # 월드 에이전트 업데이트
        for agent in self.world_agents:
            agent.tick(self.time_engine.time_scale)

        # 에이전트 간 겹침 해소 (동일한 방에 있을 때 좌표 충돌 방지)
        self.resolve_agent_overlaps()

        agent_details = self.world_view_manager.update_agent_details_view(focused_agent)
        EventBus().publish(UIEventType.BIOMETRICS_UPDATED, agent_details)

        world_details = self.world_view_manager.update_world_details_view()
        EventBus().publish(UIEventType.WORLD_DETAIL_UPDATED, world_details)

        # Pygame 시각화용 이벤트 발행
        EventBus().publish(UIEventType.WORLD_TICKED, {
            "date": self.time_engine.get_date(),
            "clock": self.time_engine.get_clock(),
            "day_cycle": self.time_engine.day_cycle,
            "season": self.time_engine.season,
            "weather": self.weather_engine.weather_type
        })

        for agent in self.world_agents:
            EventBus().publish(UIEventType.AGENT_POSITION_UPDATED, {
                "name": agent.name,
                "x": agent.position.x,
                "y": agent.position.y,
                "location": agent.location_delegate.get_current_location(),
                "is_thinking": agent.is_thinking,
                "health": agent.vital_state.health,
                "fatigue": agent.vital_state.fatigue,
                "hunger": agent.vital_state.hunger,
                "personality": agent.personality_delegate.get_matrix(),
                "relationships": agent.relationship_score_delegate.get_matrix(),
                "inventory": [obj.name for obj in agent.inventory.get_objects()]
            })

        # 이벤트 트리거
        event_objects = self.event_trigger.check_triggers(self.world_agents, self.time_engine.time_scale)
        for obj in event_objects:
            event_agent = obj[0]
            event_type = obj[1]
            event_message = obj[2]

            if event_type == EventType.FATIGUE_TRIPPED:
                if event_agent.is_thinking or not event_agent.vital_state.is_alive:
                    continue

                event_agent.push_think_event(ThinkEventType.FATIGUE, event_message, None)
                self.log_world_event(f"{event_agent.name}가 피로를 느낌.")
            
            if event_type == EventType.HUNGER_TRIPPED:
                if event_agent.is_thinking or not event_agent.vital_state.is_alive:
                    continue

                event_agent.push_think_event(ThinkEventType.HUNGER, event_message, None)
                self.log_world_event(f"{event_agent.name}가 허기를 느낌.")

            if event_type == EventType.RANDOM_SCAN:
                for agent in self.world_agents:
                    if agent.is_thinking or not agent.vital_state.is_alive:
                        continue

                    if random.random() < 0.5:
                        self.log_world_event(f"{agent.name}가 주변 탐색을 시도 함.")
                        agent.scan(event_message)

            if event_type == EventType.PROACTIVE_PULSE:
                if event_agent.is_thinking or not event_agent.vital_state.is_alive:
                    continue

                event_agent.push_think_event(ThinkEventType.PLANNING, event_message, None)
                self.log_world_event(f"{event_agent.name}가 계획 수립을 시도 함.")

            if event_type == EventType.CRITICAL_PULSE:
                if event_agent.is_thinking or not event_agent.vital_state.is_alive:
                    continue

                event_agent.push_think_event(ThinkEventType.PLANNING, event_message, None)
                self.log_world_event(f"{event_agent.name}가 고착 상황 탈출을 시도 함.")

        # 월드 에이전트 행동 결과 처리
        for agent in self.world_agents:
            if agent.think_event_queue and not agent.is_thinking:
                agent.is_thinking = True
                self.cognitive_worker.queue_agent(agent)

    def log_world_event(self, log):
        EventBus().publish(UIEventType.WORLD_LOG_APPENDED, f"[{self.time_engine.get_date()} {self.time_engine.get_clock()}] {log}")
        
        for agent in self.world_agents:
            if log.startswith(agent.name):
                short_log = self._get_short_action_label(log, agent.name)
                if short_log:
                    self.log_agent_thinking_event(agent.name, short_log)
                break

    def log_agent_thinking_event(self, agent_name, log):
        EventBus().publish(UIEventType.AGENT_THINKING_LOG_APPENDED, {
            "name": agent_name,
            "log": log
        })

    def log_system_event(self, log):
        EventBus().publish(UIEventType.SYSTEM_LOG_APPENDED, f"[{self.time_engine.get_date()} {self.time_engine.get_clock()}] {log}")
        Logger.log("[SYSTEM]", log)

    def log_agent_event(self, log):
        EventBus().publish(UIEventType.AGENT_CHAT_LOG_APPENDED, f"[{self.time_engine.get_date()} {self.time_engine.get_clock()}]\n{log}")

    def get_state_context(self):
        return f"""\
{self.time_engine.get_context()}\n
{self.weather_engine.get_context()}"""

    def set_serper_api_key(self, serper_api_key):
        self.serper_api_key = serper_api_key

    def resolve_agent_overlaps(self):
        # Group agents by location
        location_agents = {}
        for agent in self.world_agents:
            loc = agent.location_delegate.get_current_location()
            if loc:
                location_agents.setdefault(loc, []).append(agent)

        # For each location, arrange agents to prevent overlap
        for loc_name, agents in location_agents.items():
            if not agents:
                continue

            # Query the room size to find the center
            cx, cy = 4.0, 4.0
            space_obj = self.object_manager.get_object(loc_name)
            if space_obj and hasattr(space_obj, 'size'):
                cx = float(space_obj.size.x // 2)
                cy = float(space_obj.size.y // 2)

            if len(agents) == 1:
                agents[0].position.set_value(cx, cy)
            else:
                # Arrange agents in a cross/star offset pattern to prevent overlaps on integer grids.
                # Slots: Center, Left, Right, Up, Down, Diagonals
                offsets = [
                    (0.0, 0.0),
                    (-2.0, 0.0),
                    (2.0, 0.0),
                    (0.0, -2.0),
                    (0.0, 2.0),
                    (-2.0, -2.0),
                    (2.0, 2.0),
                    (-2.0, 2.0),
                    (2.0, -2.0)
                ]
                for i, agent in enumerate(agents):
                    ox, oy = offsets[i % len(offsets)]
                    ax = cx + ox
                    ay = cy + oy
                    if space_obj and hasattr(space_obj, 'size'):
                        # Keep it inside the boundary [1, size-2] to avoid touching walls
                        ax = max(1.0, min(float(space_obj.size.x - 2), ax))
                        ay = max(1.0, min(float(space_obj.size.y - 2), ay))
                    agent.position.set_value(ax, ay)

    def _get_short_action_label(self, log, agent_name):
        body = log.replace(agent_name, "").strip()
        
        if "공간으로 이동" in body:
            try:
                parts = body.split("공간으로 이동")
                if len(parts) > 0:
                    loc = parts[0].replace("가", "").replace("의", "").strip()
                    if len(loc) > 6:
                        loc = loc[:5] + ".."
                    return f"이동: {loc}"
            except Exception:
                pass
            return "공간 이동"
            
        if "이동할 수 없음" in body:
            return "이동 실패"
            
        if "휴식함" in body or "휴식 중" in body:
            return "휴식 중"
            
        if "획득" in body:
            try:
                parts = body.split("을 획득")
                if len(parts) > 0:
                    item = parts[0].replace("가", "").strip()
                    if len(item) > 6:
                        item = item[:5] + ".."
                    return f"획득: {item}"
            except Exception:
                pass
            return "아이템 획득"
            
        if "사용" in body:
            try:
                parts = body.split("을 사용")
                if len(parts) > 0:
                    item = parts[0].replace("가", "").strip()
                    if len(item) > 6:
                        item = item[:5] + ".."
                    return f"사용: {item}"
            except Exception:
                pass
            return "아이템 사용"

        if "관찰" in body:
            try:
                parts = body.split("을 관찰")
                if len(parts) > 0:
                    item = parts[0].replace("가", "").strip()
                    if len(item) > 6:
                        item = item[:5] + ".."
                    return f"관찰: {item}"
            except Exception:
                pass
            return "아이템 관찰"
            
        if "말을 걸었음" in body or "말을 걸어" in body:
            return "대화 시도"
            
        if "대화가 종료" in body:
            return "대화 종료"
            
        if "웹 검색" in body:
            return "웹 검색"
            
        if "피로를 느낌" in body or "피로" in body:
            return "피로함"
            
        if "허기를 느낌" in body or "허기" in body:
            return "배고픔"
            
        if "주변 탐색" in body or "정찰" in body or "탐색" in body:
            return "주변 정찰"
            
        if "계획 수립" in body:
            return "계획 수립"
            
        if "고착 상황 탈출" in body:
            return "고착 탈출 시도"
            
        if "완성함" in body or "제작" in body:
            try:
                if "완성함" in body:
                    parts = body.split("완성함")
                    if "'" in parts[0]:
                        item = parts[0].split("'")[-2]
                        if len(item) > 6:
                            item = item[:5] + ".."
                        return f"제작: {item}"
            except Exception:
                pass
            return "아이템 제작"
            
        if "변형함" in body:
            return "상태 변형"

        if "실패" in body:
            return "행동 실패"
            
        if "행동을 하지 않음" in body or "대기" in body:
            return "대기 중"
            
        clean_body = body.replace("가 ", "").replace("의 ", "").strip()
        if len(clean_body) <= 10:
            return clean_body
            
        return None


        