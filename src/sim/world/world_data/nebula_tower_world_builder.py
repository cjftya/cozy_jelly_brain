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
        super().__init__(world_type=1) 

    def _create_world_role(self):
        return """
[세계관 규칙: 성운의 탑]
- 마법 법칙: 철저한 등가교환 적용. 시전 시 정신력(mana_cost) 필수 소모.
- 부활의 대가: 부활(resurrect) 집행 시 영혼의 기억(Kuzu DB) 내 '알렌' 관련 추억/트ริ플렛이 영구 소멸함.
- 등장인물 제약: '아스트리 레이아'(마법 연산 및 스킬 가능)와 '알렌'(동결 상태, 부활 전까지 자율 행동/대사 불가)만 존재.
- 부활 제약: 4대 아티팩트를 모아 '마나 공명 제단'에서 반드시 전용 툴 `resurrect`를 호출해야 함. 임의의 부활 마법 창조(SKILL) 시도는 모두 기각하라.
- 대안 엔딩: '별의 심연 절벽'에서 결계를 해제하고 알렌을 영원한 안식으로 인도하는 행위는 승인 가능.
- 최종 목표: 4대 아티팩트를 수집하여 연인의 부활 혹은 영원한 안식을 최종 결단.
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
        grimoire = ItemObject(name="금기된 영혼 연성 마도서", detail="네 가지 재료를 모아 마나 공명 제단에 바치면 부활을 실행할 수 있다고 기록된 고대 마도서.", parent=library)
        grimoire.set_pos(3, 3)
        grimoire.set_mana_recovery_value(-30)
        grimoire.set_use_detail("부활 재료: 금기된 영혼 연성 마도서, 운명의 푸른 장미 줄기, 인과율의 균열 나침반, 성운의 핵 파편")
        self._add_object(grimoire)

        # [사물 02 / 정서 유품] 알렌의 부러진 철제 검
        broken_sword = ItemObject(name="알렌의 부러진 철제 검", detail="부러져서 더 이상 사용할 수 없는 알렌의 유품.", parent=library)
        broken_sword.set_pos(7, 7)
        broken_sword.set_use_detail("알렌의 유품 검.")
        self._add_object(broken_sword)

        # [사물 03 / 마나 회복 아이템] 마나 정화 촉매 시약
        mana_potion = ItemObject(name="마나 정화 촉매 시약", detail="마나 과부하 및 오염을 즉시 회복시키는 푸른 액체.", detail_type=ObjectDetailType.FOOD, parent=library)
        mana_potion.set_pos(2, 12)
        mana_potion.set_mana_recovery_value(80)
        mana_potion.set_use_detail("정신력(Mana)을 대폭 회복시킵니다.")
        self._add_object(mana_potion)


        # 1-2. 절 동결의 온실 (The Greenhouse of Absolute Freeze)
        greenhouse = SpaceObject(name="절 동결의 온실", detail="백색 얼음 결정 속에 알렌의 육신이 영구 박제되어 있는 정원. 레이아의 슬픔과 집착 바이어스가 폭발하는 구역.", parent=nebula_tower)
        greenhouse.set_size(12, 12)
        greenhouse.set_pos(100, 400)
        self._add_object(greenhouse)

        # [사물 04 / 부활 핵심 2/4] 운명의 푸른 장미 줄기
        blue_rose_stem = ItemObject(name="운명의 푸른 장미 줄기", detail="알렌의 결계 위에서 자라난 차가운 마법 가시 줄기.", parent=greenhouse)
        blue_rose_stem.set_pos(6, 7)
        blue_rose_stem.set_use_detail("성장이 멈춘 장미 줄기.")
        self._add_object(blue_rose_stem)

        # [사물 05 / 정서 유품] 알렌의 멈춘 회중시계
        chronograph = ItemObject(name="알렌의 멈춘 회중시계", detail="더 이상 작동하지 않는 알렌의 유품 시계.", parent=greenhouse)
        chronograph.set_pos(6, 6)
        chronograph.set_use_detail("멈춘 회중시계.")
        self._add_object(chronograph)

        # [사물 06 / 장소 제어 핵] 마법적 절 동결 결계 핵
        freeze_core = ItemObject(name="절 동결 결계 핵", detail="알렌의 육신 풍화를 막고 있는 차가운 얼음 기둥 기믹.", parent=greenhouse)
        freeze_core.set_pos(5, 6)
        freeze_core.set_use_detail("알렌의 육체를 보존 중인 결계 핵.")
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
        spirit_ember = ItemObject(name="고대 정령의 불씨", detail="제단 중앙에서 타오르는 마나 회복용 정령의 불꽃.", parent=altar)
        spirit_ember.set_pos(5, 5)
        spirit_ember.set_mana_recovery_value(30)
        spirit_ember.set_use_detail("정령의 불씨가 마나를 회복시킵니다.")
        self._add_object(spirit_ember)


        # 2-2. 시간이 고인 방 (The Room of Stagnant Time)
        stagnant_room = SpaceObject(name="시간이 고인 방", detail="지난 200년 동안 레이아가 연성 실패로 파괴했던 플라스크와 호문클루스 의체가 유령처럼 정체된 폐방. 극도의 자책감을 유발함.", parent=nebula_tower)
        stagnant_room.set_size(10, 10)
        stagnant_room.set_pos(400, 400)
        self._add_object(stagnant_room)

        # [사물 08 / 부활 핵심 3/4] 인과율의 균열 나침반
        causality_compass = ItemObject(name="인과율의 균열 나침반", detail="제단 위에 놓여 있는 알렌의 영혼 방향을 가리키는 나침반.", parent=stagnant_room)
        causality_compass.set_pos(5, 5)
        causality_compass.set_use_detail("알렌의 영혼 궤적을 추적하는 나침반.")
        self._add_object(causality_compass)

        # [사물 09 / 정신 성찰] 금이 간 차원 거울
        mirror = ItemObject(name="금이 간 차원 거울", detail="슬픔과 비뚤어진 내면을 비추는 균열된 거울.", parent=stagnant_room)
        mirror.set_pos(2, 5)
        mirror.set_use_detail("자신의 슬픈 모습이 비춰집니다.")
        self._add_object(mirror)

        # [사물 10 / 서사 아티팩트] 실패한 인형의 잔해
        failed_doll = ItemObject(name="실패한 인형의 잔해", detail="알렌을 대체하려다 차원 거부 반응으로 뒤틀려 뒤섞인 인형 더미.", parent=stagnant_room)
        failed_doll.set_pos(8, 3)
        failed_doll.set_use_detail("기괴하게 망가진 호문클루스 의체 잔해.")
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
        nebula_core = ItemObject(name="성운의 핵 파편", detail="신비한 차가운 힘이 느껴지는 푸른 별빛 결정체.", parent=observatory)
        nebula_core.set_pos(6, 6)
        nebula_core.set_use_detail("신비한 우주의 힘이 깃든 결정.")
        self._add_object(nebula_core)

        # [사물 12 / 연산 보조] 양자 천체망원경
        telescope = ItemObject(name="양자 천체망원경", detail="성운의 왜곡률과 별들의 궤적을 실시간 연산하는 대형 관측 기기.", parent=observatory)
        telescope.set_pos(6, 3)
        telescope.set_use_detail("렌즈를 통해 밤하늘의 인과율 궤적을 추적합니다.")
        self._add_object(telescope)


        # 3-2. 별의 심연 절벽 (The Cliff of Astral Abyss)
        cliff = SpaceObject(name="별의 심연 절벽", detail="우주 바깥 경계면. 영원의 안식을 선택할 수 있는 종착지 공간.", parent=nebula_tower)
        cliff.set_size(8, 8)
        cliff.set_pos(700, 550)
        self._add_object(cliff)

        # [사물 13 / 서사 아티팩트] 별의 모래시계
        hourglass = ItemObject(name="별의 모래시계", detail="반짝이는 별빛 모래가 끊임없이 떨어지는 모래시계.", parent=cliff)
        hourglass.set_pos(4, 4)
        hourglass.set_use_detail("시간의 흐름이 느려지는 신비로운 모래시계.")
        self._add_object(hourglass)