from sim.objects.space_object import SpaceObject
from sim.objects.building_object import BuildingObject
from sim.objects.item_object import ItemObject
from sim.object_meta.object_type import ObjectType, ObjectDetailType
from sim.world.world_data.world_builder import WorldBuilder
from sim.world.world_data.world_type import WorldType
from sim.world.weather_engine import WeatherEngine, WeatherType
from sim.world.time_engine import TimeEngine
from sim.agents.castaway import Castaway

class CastAwayWorldBuilder(WorldBuilder):

    def __init__(self):
        super().__init__(WorldType.CAST_AWAY_SIM)

    def _create_weather_engine(self):
        return WeatherEngine(weather_type=WeatherType.CLEAR, remaining_hours=3)

    def _create_time_engine(self):
        return TimeEngine(start_year=3045, start_month=6, start_day=24, start_hour=6)

    def _create_agents(self, world_system_manager):
        castaway = Castaway(world_system_manager=world_system_manager)
        self._add_agent(castaway)

    def _create_objects(self, world_system_manager):
        # [그룹] 무인도 샌드박스 대지형 영역 선언
        desert_island = BuildingObject(name="가혹한 무인도", detail="끝없는 파도와 지독한 해안 안개에 고립된 미개척 절해고도.")
        self._add_object(desert_island)

        # =================================================================
        # [안전 구역 4곳] - 에이전트가 탐색(Explore) 없이 처음부터 알고 있는 입구 지형
        # =================================================================
        
        # 1. 해안가 캠프 베이스 (Size: 10x10)
        camp = SpaceObject(name="해안가 캠프", detail="추락한 조난 잔해들로 간신히 비바람만 피할 수 있게 만든 모래사장 캠프.", parent=desert_island)
        camp.set_size(10, 10)
        camp.set_pos(100, 100)
        self._add_object(camp)

        # 2. 바위 그늘 쉼터 (Size: 6x6)
        shelter = SpaceObject(name="바위 그늘", detail="거대한 화산암 절벽 아래에 형성된 서늘하고 건조한 동굴 초입 쉼터.", parent=desert_island)
        shelter.set_size(6, 6)
        shelter.set_pos(100, 120)
        self._add_object(shelter)

        # 생존용 모닥불 배치
        campfire = ItemObject(name="간이 모닥불", detail="희미하게 명멸하며 온기를 내뿜는 모닥불. 신체를 회복할 수 있을 것 같다.", parent=shelter)
        campfire.set_pos(3.0, 3.0)
        self._add_object(campfire)

        # 3. 얕은 바닷가 해안 (Size: 12x12)
        shallow_sea = SpaceObject(name="얕은 바다", detail="파도가 잔잔하게 들이치는 해안가 입구. 투명한 바닷물이 흐른다.", parent=desert_island)
        shallow_sea.set_size(12, 12)
        shallow_sea.set_pos(120, 100)
        self._add_object(shallow_sea)

        # 4. 난파선 잔해 구역 (Size: 8x8)
        wreckage = SpaceObject(name="난파선 잔해", detail="해안 바위에 걸려 찢어진 채 썩어가는 고대 목선의 선체 파편 구역.", parent=desert_island)
        wreckage.set_size(8, 8)
        wreckage.set_pos(140, 100)
        self._add_object(wreckage)

        # 생존용 기본 식료품 야생 자원 임시 배치
        sea_water = ItemObject(name="코코넛 열매", detail="나무에서 떨어져 뒹구는 즙이 가득한 열매. 수분과 허기를 채워준다.", detail_type=ObjectDetailType.DRINK, parent=camp)
        sea_water.set_pos(2, 2)
        sea_water.set_nutri(20)
        self._add_object(sea_water)

        dried_fish = ItemObject(name="말린 생선 조각", detail="바위 위에 널어두어 수분이 완전히 날아간 훈제 생선 포.", detail_type=ObjectDetailType.FOOD, parent=camp)
        dried_fish.set_pos(5, 4)
        dried_fish.set_nutri(35)
        self._add_object(dried_fish)

        snack = ItemObject(name="과자 뭉치", detail="습기를 흡수하여 부드러워진 달콤한 비상 식량.", detail_type=ObjectDetailType.FOOD, parent=camp)
        snack.set_pos(5, 5)
        snack.set_nutri(30)
        self._add_object(snack)


        # =================================================================
        # [미지 구역 3곳] - 처음엔 인지 지도에 없어 갈 수 없고, ExploreTool로 안개를 걷어내야 함!
        # =================================================================
        
        # 미지 A. 우거진 야자수 숲 (뗏목 핵심 재료 매핑 지형)
        jungle = SpaceObject(name="우거진 야자수 숲", detail="덩굴과 아름드리 야자나무가 빽빽하게 얽혀 시야를 차단하는 숲 심부.", parent=desert_island)
        jungle.set_size(10, 10)
        jungle.set_pos(500, 500) # 좌표를 멀리 떨어트려 미지감 연출
        self._add_object(jungle)

        wood_log = ItemObject(name="단단한 통나무", detail="뗏목의 부력 뼈대로 사용하기에 안성맞춤인 밀도 높은 야자수 통나무 통.", parent=jungle)
        wood_log.set_pos(4, 5)
        self._add_object(wood_log)

        rope_vine = ItemObject(name="질긴 덩굴", detail="나무 기둥을 타고 흘러내린 가죽처럼 단단하고 유연한 야생 식물 끈.", parent=jungle)
        rope_vine.set_pos(2, 7)
        self._add_object(rope_vine)

        # 미지 B. 화산암 암석 지대 (구조 신호 불꽃용 부싯돌 실존 지형)
        volcano_cliff = SpaceObject(name="화산암 지대", detail="날카로운 화산석 파편들과 절벽 무리가 기괴하게 솟아오른 바위 언덕.", parent=desert_island)
        volcano_cliff.set_size(8, 8)
        volcano_cliff.set_pos(600, 100)
        self._add_object(volcano_cliff)

        flint_stone = ItemObject(name="부싯돌", detail="표면이 단단하고 날카로워 강하게 타격 시 거대한 스파크 불꽃을 튀기는 석영석.", parent=volcano_cliff)
        flint_stone.set_pos(4, 4)
        self._add_object(flint_stone)

        # 미지 C. 바람 부는 정찰 언덕 (구조 신호용 건조 땔감 실존 지형)
        windy_hill = SpaceObject(name="정찰 언덕", detail="섬의 전경이 한눈에 내려다보이며, 마른 바람이 강하게 몰아치는 고지대 황무지.", parent=desert_island)
        windy_hill.set_size(8, 8)
        windy_hill.set_pos(100, 700)
        self._add_object(windy_hill)

        dry_brush = ItemObject(name="마른 나뭇가지", detail="바람과 태양빛에 바싹 말라 불을 붙이면 엄청난 연기를 뿜어낼 나뭇가지 무리.", parent=windy_hill)
        dry_brush.set_pos(5, 3)
        self._add_object(dry_brush)