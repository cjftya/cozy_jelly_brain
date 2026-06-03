from sim.objects.space_object import SpaceObject
from sim.objects.building_object import BuildingObject
from sim.objects.item_object import ItemObject
from sim.object_meta.object_type import ObjectType, ObjectDetailType
from sim.world.world_data.world_builder import WorldBuilder
from sim.world.world_data.world_type import WorldType
from sim.world.weather_engine import WeatherEngine, WeatherType
from sim.world.time_engine import TimeEngine
from sim.agents.tom import Tom
from sim.agents.jain import Jain

class CastAwayWorldBuilder(WorldBuilder):

    def __init__(self):
        super().__init__(WorldType.CAST_AWAY_SIM)

    def _create_world_role(self):
        return """
[세계관: 가혹한 무인도 생존]
- 장르: 극사실주의 하드코어 생존 드라마. 마법, 초능력, SF적 요소, 기적은 절대 존재하지 않는다.
- 물리 법칙: 모든 행동은 평범한 인간의 육체적 한계 내에서 물리적/생물학적으로 설명 가능해야 한다.
- 환경과 자원: 거친 파도와 지독한 안개에 갇힌 절해고도이다. 가용한 자원은 오직 섬의 자연물(나무, 돌, 덩굴, 산딸기 등)과 해안가로 떠밀려온 난파선의 잔해(보급 궤짝, 찢어진 천, 부러진 철 조각 등)뿐이다.
- 등장인물 제약: 성인 남성 'TOM'과 어린 소녀 'JAIN'만이 존재한다. TOM은 거친 물리적 노동과 사냥이 가능하지만, JAIN은 힘이 약해 무거운 통나무를 들거나 위험한 괴력을 발휘할 수 없다. JAIN이 완력으로 불가능한 고강도 물리 행동을 시도하면 기각하라.
- 상호작용: 두 생존자 간의 교류는 대화, 위로, 원망, 물리적 상처 치료 등 지극히 인간적인 범주 내에서만 이루어진다. 텔레파시나 마법적 세뇌 같은 비현실적 정신 지배는 기각하라.
- 목적: 이 세계의 궁극적인 목표는 미지 구역을 개척하여 자원을 엮고, 뗏목을 조립하거나 구조 연기를 피워 섬을 탈출하는 것이다.
"""

    def _create_weather_engine(self):
        return WeatherEngine(weather_type=WeatherType.CLEAR, remaining_hours=3)

    def _create_time_engine(self):
        return TimeEngine(start_year=3045, start_month=6, start_day=24, start_hour=6)

    def _create_agents(self, world_system_manager):
        tom = Tom(world_system_manager=world_system_manager, brain_root_dir_path=self._world_agents_brain_db_path)
        self._add_agent(tom)
        jain = Jain(world_system_manager=world_system_manager, brain_root_dir_path=self._world_agents_brain_db_path)
        self._add_agent(jain)

    def _create_objects(self, world_system_manager):
        # [최상위 루트] 무인도 전체 영역 공간 선언
        desert_island = BuildingObject(name="가혹한 무인도", detail="끝없는 파도와 지독한 해안 안개에 고립된 절해고도. 오직 서로만을 의지해야 생존할 수 있는 고립된 공간.")
        self._add_object(desert_island)

        # =================================================================
        # LAYER 1: [해안가 캠프] - 안전과 유대감, 그리고 상시 보급의 중심지
        # =================================================================
        camp = SpaceObject(name="해안가 캠프", detail="추락한 조난 잔해들로 간신히 비바람만 피할 수 있게 만든 모래사장 캠프. 제인이 유일하게 공포를 잊고 톰 아저씨의 온기를 느낄 수 있는 베이스캠프.", parent=desert_island)
        camp.set_size(12, 12)
        camp.set_pos(100, 100)
        self._add_object(camp)

        # 풍족한 보급 궤짝
        for i in range(100):
            infinite_ration = ItemObject(
                name="식량팩",
                state="지저분한 음식",
                detail="여객선 잔해에서 떠밀려온 파손되지 않은 철제 식량보급상자에 들어있는 음식팩. 허기를 해결해 준다. 하지만 음식들이 여기저기 흩어져 있고 흙이 많이 묻어 먹기 힘들다.",
                detail_type=ObjectDetailType.FOOD,
                parent=camp
            )
            infinite_ration.set_pos(2, 2)
            infinite_ration.set_nutri(50)
            self._add_object(infinite_ration)

        # 서사적 오브젝트 A: 제인의 작은 잠자리 
        jain_bed = BuildingObject(name="제인의 야자잎 침대", detail="TOM아저씨가 손이 부르트도록 모아 온 부드러운 잎사귀들을 겹겹이 쌓고, TOM의 낡은 가죽 재킷을 이불 삼아 덮어둔 작은 잠자리. JAIN에게 정서적 안정을 주는 장소.", parent=camp)
        self._add_object(jain_bed)

        # 서사적 오브젝트 B: 톰의 급조된 작업대
        tom_workbench = BuildingObject(name="급조된 목공 작업대", detail="TOM이 해안가 유목들을 덩굴로 엮어 만든 거친 작업대. 섬 곳곳의 숨겨진 가혹한 4개 구역에서 필수 부품(통나무, 덩굴, 돛천, 키 조각)을 모두 수집해 가져와야만 최종 탈출용 뗏목(BUILD_RAFT)을 조립할 수 있다.", parent=camp)
        self._add_object(tom_workbench)


        # =================================================================
        # LAYER 2: [바위 그늘 쉼터] - 신체적 한계를 극복하기 위한 회복 기지
        # =================================================================
        shelter = SpaceObject(name="바위 그늘", detail="거대한 화산암 절벽 아래에 형성된 시원하고 건조한 암석 동굴 초입. 한낮의 잔인한 더위를 피해 피로를 풀기에 완벽한 장소.", parent=desert_island)
        shelter.set_size(6, 6)
        shelter.set_pos(100, 200)
        self._add_object(shelter)

        # LIGHT_SIGNAL_TOOL과 연동할 수 있는 구조 요청 스팟
        flint = ItemObject(name="부싯돌", detail="강하게 타격 시 스파크를 튕기는 단단한 석영석. 신호 화대 장작에 불을 붙일 수 있다.", parent=shelter)
        flint.set_pos(4, 4)
        self._add_object(flint)

        # 회복 가속용 모닥불
        campfire = ItemObject(name="생명의 모닥불", detail="TOM이 지펴놓은 따스한 모닥불. 장작 타는 소리가 동굴에 울려 퍼진다. 이 옆에서 휴식(REST)을 취하면 극심한 피로도가 빠르게 씻겨 내려간다.", parent=shelter)
        campfire.set_pos(3, 3)
        self._add_object(campfire)


        # =================================================================
        # LAYER 3: [우거진 야자수 숲] - 숨겨진 미지 구역 1 (필수 부품 1/4)
        # =================================================================
        jungle = SpaceObject(name="우거진 야자수 숲", detail="덩굴과 거대한 야자나무들이 하늘을 가려 낮에도 어두컴컴한 숲 심부. 제인에게는 공포의 대상이지만 탈출을 위한 핵심 자원이 숨겨진 첫 번째 미지 영역.", parent=desert_island)
        jungle.set_size(15, 15)
        jungle.set_pos(500, 500) 
        self._add_object(jungle)

        # 톰의 고강도 노동 오브젝트 - 필수 아이템 1/4
        wood_log = ItemObject(
            name="단단한 야자나무 통나무",
            detail="뗏목의 하부 뼈대와 핵심 부력을 담당할 거대하고 묵직한 통나무. 너무 무거워서 제인은 들 수 없으며, 오직 톰이 피로를 무릅쓰고 가져가야 하는 탈출용 뗏목의 베이스 자원.", 
            parent=jungle
        )
        wood_log.set_pos(5, 5)
        self._add_object(wood_log)

        # 제인의 감성적 창발을 유도하는 오브젝트
        for i in range(20):
            berry_bush = ItemObject(
                name="달콤한 산딸기 덤불", 
                detail="붉고 탐스러운 과일들이 알알이 맺힌 작은 덤불. 식량 상자가 있지만, 제인이 아저씨의 지친 기색을 달래주기 위해 따서 선물하고 싶어지는 정서적 유도 아이템.", 
                detail_type=ObjectDetailType.FOOD, 
                parent=jungle
            )
            berry_bush.set_pos(8, 2)
            berry_bush.set_nutri(10)
            self._add_object(berry_bush)


        # =================================================================
        # LAYER 4: [바람 부는 정찰 언덕] - 장기적 목적(구조)의 시야 확보 공간
        # =================================================================
        windy_hill = SpaceObject(name="정찰 언덕", detail="섬의 전경과 수평선 너머의 안개가 한눈에 내려다보이는 고지대 민둥산 언덕. 바람이 강하게 몰아쳐 시원하지만 고립감이 선명해지는 곳.", parent=desert_island)
        windy_hill.set_size(8, 8)
        windy_hill.set_pos(100, 700)
        self._add_object(windy_hill)

        # LIGHT_SIGNAL_TOOL과 연동할 수 있는 구조 요청 스팟
        brush = ItemObject(name="마른 나뭇가지", detail="바싹 말라 불을 붙이면 거대한 검은 연기를 뿜어낼 유목 나뭇가지 무리.", parent=windy_hill)
        brush.set_pos(4, 4)
        self._add_object(brush)


        # =================================================================
        # 🌟 NEW LAYERS: 가혹한 조건을 위한 독립된 추가 숨겨진 미지 구역들
        # =================================================================

        # 숨겨진 미지 구역 2: [안개 낀 늪지대] ──> 자원 결합용 결속선 (필수 부품 2/4)
        swamp = SpaceObject(name="안개 낀 늪지대", detail="독한 가스와 진흙 구덩이가 발목을 잡는 기괴한 해안 늪지 영역. 사방에 깔린 안개가 시야를 방해하여 극심한 피로를 유발하는 두 번째 미지 구역.", parent=desert_island)
        swamp.set_size(10, 10)
        swamp.set_pos(200, 600)
        self._add_object(swamp)

        # 제인의 조력 텍스처를 늪지대로 이식하여 서사적 연결 유지 (필수 아이템 2/4)
        rope_vine = ItemObject(
            name="질긴 야생 덩굴", 
            detail="늪지대 고목들을 타고 길게 흘러내린 가죽 같은 식물 줄기. 유연하고 단단하여 통나무들을 결속하는 데 필수적이다. 힘이 약한 제인도 아저씨를 돕기 위해 용기를 내어 채집한 뒤 선물(GIVE)할 수 있다.", 
            parent=swamp
        )
        rope_vine.set_pos(3, 4)
        self._add_object(rope_vine)


        # 숨겨진 미지 구역 3: [파도치는 절벽 해안] ──> 추진력을 얻을 돛천 (필수 부품 3/4)
        cliff_shore = SpaceObject(name="파도치는 절벽 해안", detail="날카로운 암초와 집채만 한 파도가 몰아치는 험준한 절벽 아래 해안가. 세찬 해풍이 사방에서 불어와 정찰 시 극심한 체력 소모를 요구하는 세 번째 미지 구역.", parent=desert_island)
        cliff_shore.set_size(8, 8)
        cliff_shore.set_pos(700, 300)
        self._add_object(cliff_shore)

        # 필수 아이템 3/4
        sail_canvas = ItemObject(
            name="찢어진 난파선 돛천", 
            detail="절벽 바위에 위태롭게 걸려 펄럭이던 튼튼한 천 파편. 뗏목 중심에 돛으로 매달아 거친 수평선을 뚫고 나아갈 추진력을 얻기 위한 필수 재료.", 
            parent=cliff_shore
        )
        sail_canvas.set_pos(4, 2)
        self._add_object(sail_canvas)


        # 숨겨진 미지 구역 4: [검은 화산암 동굴] ──> 방향을 전환할 키(노) (필수 부품 4/4)
        volcano_cave = SpaceObject(name="검은 화산암 동굴", detail="섬 북쪽 끝에 숨겨진 칠흑 같은 암석 동굴 내부. 한 치 앞도 보이지 않는 어둠과 기괴한 파도 울림소리가 제인을 극도로 공포에 질리게 만드는 마지막 네 번째 미지 구역.", parent=desert_island)
        volcano_cave.set_size(6, 6)
        volcano_cave.set_pos(400, 800)
        self._add_object(volcano_cave)

        # 필수 아이템 4/4
        iron_rudder = ItemObject(
            name="부러진 철제 키 조각", 
            detail="동굴 깊은 곳 밀물에 쓸려 들어와 바위 틈에 박혀 있던 철제 판자. 험한 바다 바깥으로 나갔을 때 뗏목의 방향을 제어할 키(Rudder)를 완성하기 위해 반드시 확보해야 하는 재료.", 
            parent=volcano_cave
        )
        iron_rudder.set_pos(3, 3)
        self._add_object(iron_rudder)