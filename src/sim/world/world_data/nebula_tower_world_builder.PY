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
[세계관: 성운의 탑과 영원의 서고]
- 장르: 다크 판타지 미스터리 로맨스, 인지 서사 시뮬레이션.
- 마법/인과 법칙: 모든 마법적 창조와 상태 변형은 철저한 등가교환과 마나 평형의 법칙을 따른다. 죽은 자를 되살리는 '부활'은 우주적인 금기이며, 이를 격발하기 위해서는 산 자의 뇌리(Kuzu DB) 속 모든 추억과 사랑의 트리플렛 전체를 연산 연료로 태워 영구 소멸시켜야 하는 잔인한 대가가 따른다.
- 환경과 자원: 우주의 왜곡된 시공간 경계선 위에 홀로 솟아 있는 탑의 6대 정서 구역(서고, 온실, 제단, 폐방, 관측소, 절벽)이다. 가용한 자원은 고대의 마도서들과 탑 곳곳에 숨겨진 4대 필수 서사 아티팩트(금기된 영혼 연성 마도서, 운명의 푸른 장미 줄기, 인과율의 균열 나침반, 성운의 핵 파편)뿐이다.
- 등장인물 제약: 대마법사 '아스트리 레이아'와 얼음 속에 동결되어 정지된 청년 '알렌'만이 존재한다. 레이아는 마법 연산과 스킬 격발이 가능하지만 시전 시 정신력(mana_cost)을 반드시 소모해야 하며, 알렌은 동결된 사(死)의 상태이므로 부활 마법이 성공하기 전까지는 어떠한 대사나 자율 행동도 할 수 없다.
- 상호작용 및 부활 제약: 부활을 집행하려면 4대 아티팩트를 인벤토리에 모두 모아 반드시 '마나 공명 제단'으로 이동한 뒤, 전용 권능인 'resurrect' 함수를 호출해야 한다. 이 조건 없이 임의로 부활 마법을 창조해내려는 SKILL 툴 시도는 인과율 위배로 간주하여 모두 기각하라. 반대로 '별의 심연 절벽'으로 이동하여 결계를 해제하고 알렌을 영원한 안식으로 인도하는 상호작용은 승인 가능하다.
- 목적: 이 세계의 궁극적인 목표는 탑의 각 구역을 탐색하여 4대 아티팩트를 독점하고, 세계의 진실 연산을 완수하여 연인의 부활 혹은 영원한 안식을 최종 결단하는 것이다.
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
        grimoire = ItemObject(name="금기된 영혼 연성 마도서", detail="(부활의 핵심 재료 1/4) 마도서의 지식이 담겨있는 고대 책. 읽을 수록 정신이 오염된다.", parent=library)
        grimoire.set_pos(3, 3)
        grimoire.set_mana_recovery_value(-30)
        grimoire.set_use_detail("네 가지의 핵심 재료('금기된 영혼 연성 마도서', '운명의 푸른 장미 줄기', '인과율의 균열 나침반', '성운의 핵 파편') 를 모아 마나 공명 제단에 바치면 부활의 힘을 얻을 수 있다.")
        self._add_object(grimoire)

        # [사물 02 / 정서 유품] 알렌의 부러진 철제 검
        broken_sword = ItemObject(name="알렌의 부러진 철제 검", detail="200년 전 알렌이 그녀를 구하다 차원 괴수의 발톱에 부러뜨린 검.", parent=library)
        broken_sword.set_pos(7, 7)
        broken_sword.set_use_detail("알렌의 유품. 부러져서 더이상 사용할 수 없다.")
        self._add_object(broken_sword)

        # [사물 03 / 마나 회복 아이템] 마나 정화 촉매 시약
        mana_potion = ItemObject(name="마나 정화 촉매 시약", detail="시약을 직접 복용하거나, 마법 재료에 섞어 연소시켜 폭발을 막는 데 사용할 수 있는 푸른 액체.", detail_type=ObjectDetailType.FOOD, parent=library)
        mana_potion.set_pos(2, 12)
        mana_potion.set_mana_recovery_value(80)
        mana_potion.set_use_detail("마나 과부하 및 오염도를 즉시 중화하여 회복시켜 주는 유일한 연금술 촉매제.")
        self._add_object(mana_potion)


        # 1-2. 절 동결의 온실 (The Greenhouse of Absolute Freeze)
        greenhouse = SpaceObject(name="절 동결의 온실", detail="백색 얼음 결정 속에 알렌의 육신이 영구 박제되어 있는 정원. 레이아의 슬픔과 집착 바이어스가 폭발하는 구역.", parent=nebula_tower)
        greenhouse.set_size(12, 12)
        greenhouse.set_pos(100, 400)
        self._add_object(greenhouse)

        # [사물 04 / 부활 핵심 2/4] 운명의 푸른 장미 줄기
        blue_rose_stem = ItemObject(name="운명의 푸른 장미 줄기", detail="(부활의 핵심 재료 2/4) 알렌의 가슴 위 얼음 결계를 뚫고 자라난 차가운 마법 가시 줄기.", parent=greenhouse)
        blue_rose_stem.set_pos(6, 7)
        blue_rose_stem.set_use_detail("너무 오래되어서 더이상 자라나지 않는다.")
        self._add_object(blue_rose_stem)

        # [사물 05 / 정서 유품] 알렌의 멈춘 회중시계
        chronograph = ItemObject(name="알렌의 멈춘 회중시계", detail="알렌의 유품.", parent=greenhouse)
        chronograph.set_pos(6, 6)
        chronograph.set_use_detail("너무 오래되어서 더이상 작동하지 않는다.")
        self._add_object(chronograph)

        # [사물 06 / 장소 제어 핵] 마법적 절 동결 결계 핵
        freeze_core = ItemObject(name="절 동결 결계 핵", detail="알렌의 육신이 풍화되는 것을 막기 위한 푸른 얼음 기둥.", parent=greenhouse)
        freeze_core.set_pos(5, 6)
        freeze_core.set_use_detail("엄청 차갑지만 알렌의 육체는 완벽하게 보존되고있다.")
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
        spirit_ember = ItemObject(name="고대 정령의 불씨", detail="제단 중앙에서 타오르고있는 정령의 불꽃.", parent=altar)
        spirit_ember.set_pos(5, 5)
        spirit_ember.set_mana_recovery_value(30)
        spirit_ember.set_use_detail("정령의 불씨가 마나를 회복시킨다.")
        self._add_object(spirit_ember)


        # 2-2. 시간이 고인 방 (The Room of Stagnant Time)
        stagnant_room = SpaceObject(name="시간이 고인 방", detail="지난 200년 동안 레이아가 연성 실패로 파괴했던 플라스크와 호문클루스 의체가 유령처럼 정체된 폐방. 극도의 자책감을 유발함.", parent=nebula_tower)
        stagnant_room.set_size(10, 10)
        stagnant_room.set_pos(400, 400)
        self._add_object(stagnant_room)

        # [사물 08 / 부활 핵심 3/4] 인과율의 균열 나침반
        causality_compass = ItemObject(name="인과율의 균열 나침반", detail="(부활의 핵심 재료 3/4) 제단 위에 놓여져있는 영혼을 가르키는 나침반.", parent=stagnant_room)
        causality_compass.set_pos(5, 5)
        causality_compass.set_use_detail("알렌의 영혼이 있는 곳을 가르킨다.")
        self._add_object(causality_compass)

        # [사물 09 / 정신 성찰] 금이 간 차원 거울
        mirror = ItemObject(name="금이 간 차원 거울", detail="균열이 간 차원의 거울. 여러 모습이 비춰진다.", parent=stagnant_room)
        mirror.set_pos(2, 5)
        mirror.set_use_detail("균열 사이로 자신의 비뚤어진 모습과 슬픔에 잠긴 자신의 모습이 비춰진다.")
        self._add_object(mirror)

        # [사물 10 / 서사 아티팩트] 실패한 인형의 잔해
        failed_doll = ItemObject(name="실패한 인형의 잔해", detail="알렌을 대체하려다 차원의 인과율적 거부 반응으로 기괴하게 뒤틀려 산산조각 난 인형무더기.", parent=stagnant_room)
        failed_doll.set_pos(8, 3)
        failed_doll.set_use_detail("당신을 대체하려다 산산조각 난 인형. 끔찍하고 처참한 모습에서 거부감이 느껴진다.")
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
        nebula_core = ItemObject(name="성운의 핵 파편", detail="(부활의 핵심 재료 4/4) 관측소 난간에 놓여진 푸른 별빛 결정체.", parent=observatory)
        nebula_core.set_pos(6, 6)
        nebula_core.set_use_detail("만지면 차갑고 신비한 힘이 느껴진다.")
        self._add_object(nebula_core)

        # [사물 12 / 연산 보조] 양자 천체망원경
        telescope = ItemObject(name="양자 천체망원경", detail="칠흑 같은 성운의 왜곡률과 별빛 궤적을 실시간 연산하는 거대 관측 기기.", parent=observatory)
        telescope.set_pos(6, 3)
        telescope.set_use_detail("거대한 렌즈를 통해 밤하늘을 볼 수 있다. 별들의 궤적을 추적하며 인과율을 계산하는 듯하다.")
        self._add_object(telescope)


        # 3-2. 별의 심연 절벽 (The Cliff of Astral Abyss)
        cliff = SpaceObject(name="별의 심연 절벽", detail="성운의 잔해가 파도처럼 일렁이는 우주의 바깥 경계면. 과거의 유령을 별빛으로 승화시켜 영원한 안식을 선택할 종착지 공간.", parent=nebula_tower)
        cliff.set_size(8, 8)
        cliff.set_pos(700, 550)
        self._add_object(cliff)

        # [사물 13 / 서사 아티팩트] 별의 모래시계
        hourglass = ItemObject(name="별의 모래시계", detail="빛나는 모래가 끝임없이 떨어지는 유리병.", parent=cliff)
        hourglass.set_pos(4, 4)
        hourglass.set_use_detail("유리병 속 모래는 밤하늘의 별빛처럼 반짝인다. 모래가 떨어지는 속도는 점점 느려지는 것 같다.")
        self._add_object(hourglass)