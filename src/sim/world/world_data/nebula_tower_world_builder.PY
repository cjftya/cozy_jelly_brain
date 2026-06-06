from sim.objects.space_object import SpaceObject
from sim.objects.building_object import BuildingObject
from sim.objects.item_object import ItemObject
from sim.object_meta.object_type import ObjectType, ObjectDetailType
from sim.world.world_data.world_builder import WorldBuilder
from sim.world.weather_engine import WeatherEngine, WeatherType
from sim.world.time_engine import TimeEngine
from sim.agents.astri_leia import AstriLeia
from sim.agents.allen import Allen

class NebulaTowerWorldBuilder(WorldBuilder):
    def __init__(self):
        # WorldType.NEBULA_TOWER_SIM = 1 로 델리게이트 바인딩
        super().__init__(world_type=1) 

    def _create_world_role(self):
        return """
[세계관 대서사: 성운의 탑 — 영원과 필멸의 경계선]
- 장르: 다크 판타지 미스터리 로맨스, 인지 서사 시뮬레이션.
- 코어 인과율: 우주의 마법은 철저한 등가교환과 마나 평형의 지배를 받는다. 금기를 깨는 권능은 무한하지 않으며 영혼을 마모시킨다.
- 부활의 인과적 족쇄 (Resurrection Matrix):
  '절 동결의 온실'에 멈춰 서 있는 연인 '알렌'을 다시 숨 쉬게 하려면, 탑 전역에 흩어진 [4대 핵심 서사 아티팩트]를 완벽히 독점해야만 한다.
  1. 영원의 서고 ──> [금기된 영혼 연성 마도서] (영혼의 형태를 빚는 인과율의 공식)
  2. 절 동결의 온실 ──> [운명의 푸른 장미 줄기] (생사의 경계를 묶은 마법적 생명줄)
  3. 시간이 고인 방 ──> [인과율의 균열 나침반] (부서진 영혼의 파편이 고인 좌표계)
  4. 별빛 관측소 ──> [성운의 핵 파편] (차원의 거부 반응을 억누를 푸른 결정체)
- 실행 및 파멸의 조건:
  4개의 아티팩트를 'take' 도구로 인벤토리에 모두 모아 [마나 공명 제단]의 중심부에서 최종 권능(resurrect)을 격발하라.
  마법이 완성되는 순간, 등가교환의 법칙에 따라 아스트리 레이아의 뇌리(Kuzu DB) 속 알렌과의 200년 추억은 전부 불타 소멸하여 낯선 이로 마주하게 된다.
- 안식의 대안 분기:
  부활을 포기하고 [별의 심연 절벽]으로 향해 연인의 결계를 완전히 해제(object_transform)하여 그를 안식으로 인도하고, 추억을 품은 채 홀로 당당히 나아가는 길 또한 고결한 해피엔딩이다.
"""

    def _create_weather_engine(self):
        # 상층부 개방 구역에서의 정서 자극 극대화를 위한 초정밀 날씨 초기화
        return WeatherEngine(weather_type=WeatherType.CLEAR, remaining_hours=6)

    def _create_time_engine(self):
        # 엉겁의 긴 세월을 증명하는 아스트리 레이아 전용 시간축 (7012년선)
        return TimeEngine(start_year=7012, start_month=1, start_day=1, start_hour=0)

    def _create_agents(self, world_system_manager):
        # 비동기 인지 워커 스레드와 결합할 두 남녀 에이전트 생성 및 주입
        self._add_agent(AstriLeia(world_system_manager=world_system_manager, brain_root_dir_path=self._world_agents_brain_db_path))
        self._add_agent(Allen(world_system_manager=world_system_manager, brain_root_dir_path=self._world_agents_brain_db_path))

    def _create_objects(self, world_system_manager):
        # [최상위 물리 루트 루트] 성운의 탑
        nebula_tower = BuildingObject(name="성운의 탑", detail="우주의 왜곡된 시공간 경계선 위에 홀로 솟아 있는 거대한 고독의 아카이브.")
        self._add_object(nebula_tower)

        # =================================================================
        # 🏛️ LAYER 1: 하층부 — 차가운 이성과 멈춰버린 집착의 대립선
        # =================================================================
        
        # 1-1. 영원의 서고 (The Library of Eternity)
        library = SpaceObject(name="영원의 서고", detail="수천 년의 금기 기록과 별빛 연산 장치가 가득한 지하 서고. 레이아의 주 거처이자 인지 마모가 일어나는 공간.", parent=nebula_tower)
        library.set_size(15, 15)
        library.set_pos(100, 100)
        self._add_object(library)

        # [사물 01 / 부활 핵심 1/4] 금기된 영혼 연성 마도서
        grimoire = ItemObject(name="금기된 영혼 연성 마도서", detail="알렌의 영혼을 역연성하는 금단의 공식이 흐르는 고대 책. 읽을수록 진실을 일깨우나 마나 평형을 무너뜨린다.", parent=library)
        grimoire.set_pos(3, 3)
        self._add_object(grimoire)

        # [사물 02 / 정서 유품] 알렌의 부러진 철제 검
        broken_sword = ItemObject(name="알렌의 부러진 철제 검", detail="200년 전 알렌이 그녀를 구하다 차원 괴수의 발톱에 부러뜨린 검. 조사 시 죄책감과 사명감 유발.", parent=library)
        broken_sword.set_pos(7, 7)
        self._add_object(broken_sword)

        # [사물 03 / 생존 소모품] 마나 정화 촉매 시약
        mana_potion = ItemObject(name="마나 정화 촉매 시약", detail="마나 과부하 및 오염도(Hunger 슬롯)를 즉시 중화하여 회복시켜 주는 유일한 연금술 촉매제.", detail_type=ObjectDetailType.FOOD, parent=library)
        mana_potion.set_pos(2, 12)
        mana_potion.set_nutri(45) # Use_Tool 가동 시 마나 안정도 복구량
        self._add_object(mana_potion)


        # 1-2. 절 동결의 온실 (The Greenhouse of Absolute Freeze)
        greenhouse = SpaceObject(name="절 동결의 온실", detail="백색 얼음 결정 속에 알렌의 육신이 영구 박제되어 있는 정원. 레이아의 슬픔과 집착 바이어스가 폭발하는 구역.", parent=nebula_tower)
        greenhouse.set_size(12, 12)
        greenhouse.set_pos(100, 400)
        self._add_object(greenhouse)

        # [사물 04 / 부활 핵심 2/4] 운명의 푸른 장미 줄기
        blue_rose_stem = ItemObject(name="운명의 푸른 장미 줄기", detail="알렌의 가슴 위 얼음 결계를 뚫고 자라난 차가운 마법 가시 줄기. 부활 연성의 핵심 골격 재료.", parent=greenhouse)
        blue_rose_stem.set_pos(6, 7)
        self._add_object(blue_rose_stem)

        # [사물 05 / 정서 유품] 알렌의 멈춘 회중시계
        chronograph = ItemObject(name="알렌의 멈춘 회중시계", detail="알렌의 심장이 정지했던 200년 전 그 새벽의 시간에 바늘이 영구 고정되어 버린 아스라한 유품.", parent=greenhouse)
        chronograph.set_pos(6, 6)
        self._add_object(chronograph)

        # [사물 06 / 장소 제어 핵] 마법적 절 동결 결계 핵
        freeze_core = ItemObject(name="절 동결 결계 핵", detail="알렌의 육신이 풍화되는 것을 막기 위해 온실 전체의 시간선을 강제로 묶어두고 있는 푸른 얼음 기둥.", parent=greenhouse)
        freeze_core.set_pos(5, 6)
        self._add_object(freeze_core)


        # =================================================================
        # ⚡ LAYER 2: 중층부 — 위험한 도약의 제단과 왜곡된 실패의 흔적
        # =================================================================
        
        # 2-1. 마나 공명 제단 (The Altar of Mana Resonance)
        altar = SpaceObject(name="마나 공명 제단", detail="4대 아티팩트를 소모하여 인과율을 거스르는 최종 부활 권능(resurrect)을 집행할 수 있는 유일한 의식의 석조 제단.", parent=nebula_tower)
        altar.set_size(10, 10)
        altar.set_pos(400, 100)
        self._add_object(altar)

        # [사물 07 / 마법 촉매] 고대 정령의 불씨
        spirit_ember = ItemObject(name="고대 정령의 불씨", detail="제단에서 정교한 상위 스킬(Skill)을 구사하거나 조합할 때 결계의 성공 유틸리티를 높여주는 마법 불꽃.", parent=altar)
        spirit_ember.set_pos(5, 5)
        self._add_object(spirit_ember)


        # 2-2. 시간이 고인 방 (The Room of Stagnant Time)
        stagnant_room = SpaceObject(name="시간이 고인 방", detail="지난 200년 동안 레이아가 연성 실패로 파괴했던 플라스크와 호문클루스 의체가 유령처럼 정체된 폐방. 극도의 자책감을 유발함.", parent=nebula_tower)
        stagnant_room.set_size(10, 10)
        stagnant_room.set_pos(400, 400)
        self._add_object(stagnant_room)

        # [사물 08 / 부활 핵심 3/4] 인과율의 균열 나침반
        causality_compass = ItemObject(name="인과율의 균열 나침반", detail="이 세계선에서 부서진 알렌의 유령 영혼 파편이 고여 있는 차원 좌표를 실시간 추적하여 지시하는 나침반.", parent=stagnant_room)
        causality_compass.set_pos(5, 5)
        self._add_object(causality_compass)

        # [사물 09 / 정신 성찰] 금이 간 차원 거울
        mirror = ItemObject(name="금이 간 차원 거울", detail="자신의 비틀린 무의식 심부와 마모 상태를 투영하는 거울. 사용 시 스스로의 성격 매트릭스를 성찰하는 독백 유도.", parent=stagnant_room)
        mirror.set_pos(2, 5)
        self._add_object(mirror)

        # [사물 10 / 서사 아티팩트] 실패한 인형의 잔해
        failed_doll = ItemObject(name="실패한 인형의 잔해", detail="알렌을 대체하려다 차원의 인과율적 거부 반응으로 기괴하게 뒤틀려 산산조각 난 인간형 도자기 의체의 흔적.", parent=stagnant_room)
        failed_doll.set_pos(8, 3)
        self._add_object(failed_doll)


        # =================================================================
        # 🔭 LAYER 3: 최상층 및 외곽 — 인과율의 판독과 종막의 선택지
        # =================================================================
        
        # 3-1. 별빛 관측소 (The Starlight Observatory)
        observatory = SpaceObject(name="별빛 관측소", detail="탑 최상층에 위치하여 외부 날씨 기류의 영향을 정직하게 받는 개방 데크. 천체 연산을 통해 진실을 도출하는 구역.", parent=nebula_tower)
        observatory.set_size(12, 12)
        observatory.set_pos(700, 250)
        self._add_object(observatory)

        # [사물 11 / 부활 핵심 4/4] 성운의 핵 파편
        nebula_core = ItemObject(name="성운의 핵 파편", detail="최종 연성 격발 시 밀려올 차원의 역류와 우주의 거부 반응을 억누르고 결계를 격리해 줄 푸른 별빛의 융합 결정체.", parent=observatory)
        nebula_core.set_pos(6, 6)
        self._add_object(nebula_core)

        # [사물 12 / 연산 보조] 양자 천체망원경
        telescope = ItemObject(name="양자 천체망원경", detail="칠흑 같은 성운의 왜곡률과 별빛 궤적을 실시간 연산하여 공백의 마도서의 락(Lock)을 해독하는 거대 관측 기기.", parent=observatory)
        telescope.set_pos(6, 3)
        self._add_object(telescope)


        # 3-2. 별의 심연 절벽 (The Cliff of Astral Abyss)
        cliff = SpaceObject(name="별의 심연 절벽", detail="성운의 잔해가 파도처럼 일렁이는 우주의 바깥 경계면. 과거의 유령을 별빛으로 승화시켜 영원한 안식을 선택할 종착지 공간.", parent=nebula_tower)
        cliff.set_size(8, 8)
        cliff.set_pos(700, 550)
        self._add_object(cliff)

        # [사물 13 / 서사 아티팩트] 별의 모래시계
        hourglass = ItemObject(name="별의 모래시계", detail="마법사로서 살아갈 영원의 무상한 시간선과 남은 고독의 깊이를 푸른 성운의 모래로 떨어뜨리는 시간의 아티팩트.", parent=cliff)
        hourglass.set_pos(4, 4)
        self._add_object(hourglass)