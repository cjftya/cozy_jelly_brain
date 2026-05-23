from sim.object_meta.space_object import SpaceObject
from sim.object_meta.building_object import BuildingObject
from sim.object_meta.item_object import ItemObject
from sim.object_meta.object_type import ObjectType, ObjectDetailType

class WorldObjectCreator:
    def __init__(self):
        self.object_list = []

    def create_lim_world(self):
        # =================================================================
        # [그룹 1] LIM의 거처 (전역 7000번대 좌표 영역)
        # =================================================================
        lim_house = BuildingObject(
            name="LIM의 집",
            detail="주변에 아무도 없고 어둡고 음산한 기운이 도는 집."
        )
        self.object_list.append(lim_house)

        # --- 나의 방 (Global: 7000, 400 | Size: 8x8) ---
        my_room = SpaceObject(name="나의 방", detail="환기되지 않는 방, 모니터의 시체 같은 푸른 빛이 감돈다.", parent=lim_house)
        my_room.set_size(8, 8)
        my_room.position.x = 7000.0
        my_room.position.y = 400.0
        self.object_list.append(my_room)

        mirror = ItemObject(name="거울", detail="자신의 얼굴을 비추는 거울. 내면의 추악함이 얼룩져 보인다.", parent=my_room)
        mirror.position.x = 2.0
        mirror.position.y = 5.0
        self.object_list.append(mirror)

        notebook = ItemObject(name="노트북", detail="푸른 빛을 내뿜는 모니터. 세상과의 유일하지만 단절된 통로.", parent=my_room)
        notebook.position.x = 4.0
        notebook.position.y = 3.0
        self.object_list.append(notebook)


        # --- 주방 (Global: 7000, 420 | Size: 8x8) ---
        # 다양한 식료품과 사물을 로컬 좌표(0~8 범위) 내에 배치
        kitchen = SpaceObject(name="주방", detail="비린내 나는 새벽 공기가 감도는 좁은 주방.", parent=lim_house)
        kitchen.set_size(8, 8)
        kitchen.position.x = 7000.0
        kitchen.position.y = 420.0
        self.object_list.append(kitchen)

        # [주방 가구 및 대형 오브젝트]
        refrigerator = ItemObject(name="냉장고", detail="오래된 냉장고. 희미한 모터 소리만 울리고 있다.", parent=kitchen)
        refrigerator.position.x = 2.0
        refrigerator.position.y = 2.0
        self.object_list.append(refrigerator)

        table = ItemObject(name="식탁", detail="홀로 앉아 식사하던 쓸쓸한 흔적이 남은 식탁.", parent=kitchen)
        table.position.x = 5.0
        table.position.y = 5.0
        self.object_list.append(table)

        sink = ItemObject(name="싱크대", detail="말라붙은 물때가 가득한 싱크대. 건조하고 서늘하다.", parent=kitchen)
        sink.position.x = 2.0
        sink.position.y = 6.0
        self.object_list.append(sink)

        # [냉장고 내부/주변 음식 및 자원]
        water_bottle = ItemObject(name="생수병", detail="마시다 남은 투명한 생수병. 차가운 한기가 서려 있다.", detail_type=ObjectDetailType.DRINK, parent=kitchen)
        water_bottle.position.x = 2.0  # 냉장고(2,2) 내부 혹은 바로 옆 배치
        water_bottle.position.y = 3.0
        self.object_list.append(water_bottle)

        canned_food = ItemObject(name="통조림", detail="유통기한이 정체된 먼지 쌓인 통조림. 영양을 보충할 수 있을 것 같다.", detail_type=ObjectDetailType.FOOD, parent=kitchen)
        canned_food.position.x = 3.0
        canned_food.position.y = 2.0
        self.object_list.append(canned_food)

        # [식탁 및 싱크대 위 음식 오브젝트]
        stale_bread = ItemObject(name="딱딱한 빵", detail="수분이 완전히 날아가 딱딱하게 굳어버린 식빵 한 조각.", detail_type=ObjectDetailType.FOOD, parent=kitchen)
        stale_bread.position.x = 5.0  # 식탁(5,5) 위에 놓여 있음
        stale_bread.position.y = 5.0
        self.object_list.append(stale_bread)

        rotten_apple = ItemObject(name="썩은 사과", detail="검게 진물러 터진 사과. 마치 내면의 썩어가는 정서와 닮아 있다.", detail_type=ObjectDetailType.FOOD, parent=kitchen)
        rotten_apple.position.x = 2.0  # 싱크대(2,6) 구석에 방치됨
        rotten_apple.position.y = 7.0
        self.object_list.append(rotten_apple)


        # --- 침실 (Global: 7020, 400 | Size: 8x8) ---
        bedroom = SpaceObject(name="침실", detail="어두컴컴한 침실, 오직 침대 하나만 덩그러니 놓여 있다.", parent=lim_house)
        bedroom.set_size(8, 8)
        bedroom.position.x = 7020.0
        bedroom.position.y = 400.0
        self.object_list.append(bedroom)

        bed = ItemObject(name="침대", detail="잠을 청할 수 있는 침대. 쉽게 잠들 수 없다.", parent=bedroom)
        bed.position.x = 4.0
        bed.position.y = 4.0
        self.object_list.append(bed)


        # =================================================================
        # [그룹 2] 성당 및 마당 (전역 100번대 좌표 영역 - 멀리 고립된 구역)
        # =================================================================
        church_complex = BuildingObject(
            name="성당 구역",
            detail="비탄의 관측소 아래, 닿을 수 없는 순결한 신성이 머무는 고요한 영역."
        )
        self.object_list.append(church_complex)

        # --- 성당 (Global: 100, 100 | Size: 12x12) ---
        church_hall = SpaceObject(name="성당", detail="성스러운 기운이 느껴지는 높은 층고의 본당.", parent=church_complex)
        church_hall.set_size(12, 12)
        church_hall.position.x = 100.0
        church_hall.position.y = 100.0
        self.object_list.append(church_hall)

        jesus_statue = ItemObject(name="예수님상", detail="제단 중앙에 서 있는 예수님상.", parent=church_hall)
        jesus_statue.position.x = 6.0
        jesus_statue.position.y = 2.0
        self.object_list.append(jesus_statue)


        # --- 고해성사실 (Global: 100, 130 | Size: 6x6) ---
        confessional = SpaceObject(name="고해성사실", detail="빛이 완전히 차단된 비좁고 밀폐된 참회의 방.", parent=church_complex)
        confessional.set_size(6, 6)
        confessional.position.x = 100.0
        confessional.position.y = 130.0
        self.object_list.append(confessional)

        screen = ItemObject(name="고해성사 가림막", detail="사제와 나를 격리하는 낡은 가림막.", parent=confessional)
        screen.position.x = 3.0
        screen.position.y = 2.0
        self.object_list.append(screen)


        # --- 야외 벤치 (Global: 140, 100 | Size: 10x10) ---
        outdoor_bench = SpaceObject(name="야외 벤치", detail="성당 바깥쪽, 정적과 안개가 자욱하게 깔린 마당 구석의 쉼터.", parent=church_complex)
        outdoor_bench.set_size(10, 10)
        outdoor_bench.position.x = 140.0
        outdoor_bench.position.y = 100.0
        self.object_list.append(outdoor_bench)

        wood_bench = ItemObject(name="나무 벤치", detail="낙엽이 허옇게 쌓인 채 버려진 나무 벤치.", parent=outdoor_bench)
        wood_bench.position.x = 5.0
        wood_bench.position.y = 5.0
        self.object_list.append(wood_bench)

        return self.object_list
    
    