from sim.objects.space_object import SpaceObject
from sim.objects.building_object import BuildingObject
from sim.objects.item_object import ItemObject
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
        my_room.set_pos(7000, 400)
        self.object_list.append(my_room)

        mirror = ItemObject(name="거울", detail="자신의 얼굴을 비추는 거울. 내면의 추악함이 얼룩져 보인다.", parent=my_room)
        mirror.set_pos(2.0, 5.0)
        mirror.set_state_machine(
            states=["CLEAN", "DIRTY"],
            state_details={
                "CLEAN": "아주 맑은 유리 표면에 지금 내 얼굴이 그대로 비친다. 흠잡을 데 없는 완벽한 비주얼이다.",
                "DIRTY": "거울 표면에 손자국과 먼지가 뒤섞여 나의 썩어가는 얼굴을 더럽힌다."
            }
        )
        self.object_list.append(mirror)

        notebook = ItemObject(name="노트북", detail="푸른 빛을 내뿜는 모니터. 세상과의 유일하지만 단절된 통로.", parent=my_room)
        notebook.set_pos(4.0, 3.0)
        notebook.set_state_machine(
            states=["OFF", "ON", "ERROR"],
            state_details={
                "OFF": "전원이 꺼져 있어 칠흑 같은 화면에 내 추악한 얼굴이 어렴풋이 비친다.",
                "ON": "화면이 켜지며 고대 아카이브 시스템 로그 데이터 스트림이 푸르게 명멸한다.",
                "ERROR": "파란 에러 화면(BSOD)과 함께 무차별적인 경고음 노이즈가 방 안에 울려 퍼진다."
            }
        )
        self.object_list.append(notebook)


        # --- 주방 (Global: 7000, 420 | Size: 8x8) ---
        # 다양한 식료품과 사물을 로컬 좌표(0~8 범위) 내에 배치
        kitchen = SpaceObject(name="주방", detail="비린내 나는 새벽 공기가 감도는 좁은 주방.", parent=lim_house)
        kitchen.set_size(8, 8)
        kitchen.set_pos(7000, 420)
        self.object_list.append(kitchen)

        # [주방 가구 및 대형 오브젝트]
        refrigerator = ItemObject(name="냉장고", detail="오래된 냉장고. 희미한 모터 소리만 울리고 있다.", parent=kitchen)
        refrigerator.set_pos(2, 2)
        refrigerator.set_state_machine(
            states=["OPEN", "CLOSED"],
            state_details={
                "OPEN": "차가운 냉기가 몰아치며 속 깊은 어둠을 드러낸다.",
                "CLOSED": "철제 문이 굳게 닫혀 내부의 공허와 부패를 숨기고 있다."
            }
        )
        self.object_list.append(refrigerator)

        table = ItemObject(name="식탁", detail="홀로 앉아 식사하던 쓸쓸한 흔적이 남은 식탁.", parent=kitchen)
        table.set_pos(5, 5)
        self.object_list.append(table)

        sink = ItemObject(name="싱크대", detail="말라붙은 물때가 가득한 싱크대. 건조하고 서늘하다.", parent=kitchen)
        sink.set_pos(2, 6)
        sink.set_state_machine(
            states=["CLEAN", "DRY", "DIRTY", "STAINED"],
            state_details={
                "CLEAN": "새것처럼 빛나는 크롬 표면에 물때 하나 없이 완벽한 위생 상태를 자랑한다.",
                "DRY": "표면은 건조하지만 깊은 물때 자국이 얼룩처럼 남아있어 예전의 흔적을 고스란히 보여준다.",
                "DIRTY": "식재료 찌꺼기와 물때가 뒤섞여 지저분하고 비위생적인 상태다.",
                "STAINED": "액체가 말라붙어 검붉은 얼룩이 거뭇하게 번져있다."
            }
        )
        self.object_list.append(sink)

        # [냉장고 내부/주변 음식 및 자원]
        water_bottle = ItemObject(name="생수병", detail="마시다 남은 투명한 생수병. 차가운 한기가 서려 있다.", detail_type=ObjectDetailType.DRINK, parent=kitchen)
        water_bottle.set_pos(2, 3)
        self.object_list.append(water_bottle)

        canned_food = ItemObject(name="통조림", detail="유통기한이 정체된 먼지 쌓인 통조림. 영양을 보충할 수 있을 것 같다.", detail_type=ObjectDetailType.FOOD, parent=kitchen)
        canned_food.set_pos(3, 2)
        self.object_list.append(canned_food)

        # [식탁 및 싱크대 위 음식 오브젝트]
        stale_bread = ItemObject(name="딱딱한 빵", detail="수분이 완전히 날아가 딱딱하게 굳어버린 식빵 한 조각.", detail_type=ObjectDetailType.FOOD, parent=kitchen)
        stale_bread.set_pos(5, 5)
        self.object_list.append(stale_bread)

        rotten_apple = ItemObject(name="썩은 사과", detail="검게 진물러 터진 사과. 마치 내면의 썩어가는 정서와 닮아 있다.", detail_type=ObjectDetailType.FOOD, parent=kitchen)
        rotten_apple.set_pos(2, 7)
        self.object_list.append(rotten_apple)


        # --- 침실 (Global: 7020, 400 | Size: 8x8) ---
        bedroom = SpaceObject(name="침실", detail="어두컴컴한 침실, 오직 침대 하나만 덩그러니 놓여 있다.", parent=lim_house)
        bedroom.set_size(8, 8)
        bedroom.set_pos(7020, 400)
        self.object_list.append(bedroom)

        bed = ItemObject(name="침대", detail="잠을 청할 수 있는 침대. 쉽게 잠들 수 없다.", parent=bedroom)
        bed.set_pos(4, 4)
        bed.set_state_machine(
            states=["ORGANIZE", "FLIPPED"],
            state_details={
                "ORGANIZE": "이불이 가지런히 정돈되어 누울 준비가 되어 있다.",
                "FLIPPED": "이불이 뒤집어져 엉망이다. 누군가 막 뒤집어 놓은 것 같다."
            }
        )
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
        church_hall.set_pos(100, 100)
        self.object_list.append(church_hall)

        jesus_statue = ItemObject(name="예수님상", detail="제단 중앙에 서 있는 예수님상.", parent=church_hall)
        jesus_statue.set_pos(6, 2)
        self.object_list.append(jesus_statue)


        # --- 고해성사실 (Global: 100, 130 | Size: 6x6) ---
        confessional = SpaceObject(name="고해성사실", detail="빛이 완전히 차단된 비좁고 밀폐된 참회의 방.", parent=church_complex)
        confessional.set_size(6, 6)
        confessional.set_pos(100, 130)
        self.object_list.append(confessional)

        screen = ItemObject(name="고해성사 가림막", detail="사제와 나를 격리하는 낡은 가림막.", parent=confessional)
        screen.set_pos(3, 2)
        self.object_list.append(screen)

        # --- 야외 벤치 (Global: 140, 100 | Size: 10x10) ---
        outdoor_bench = SpaceObject(name="야외 벤치", detail="성당 바깥쪽, 정적과 안개가 자욱하게 깔린 마당 구석의 쉼터.", parent=church_complex)
        outdoor_bench.set_size(10, 10)
        outdoor_bench.set_pos(140, 100)
        self.object_list.append(outdoor_bench)


        wood_bench = ItemObject(name="나무 벤치", detail="낙엽이 허옇게 쌓인 채 버려진 나무 벤치.", parent=outdoor_bench)
        wood_bench.set_pos(5, 5)
        wood_bench.set_state_machine(
            states=["CLEAN", "DIRTY", "WET"],
            state_details={
                "CLEAN": "새것처럼 칠해져 있으며 먼지 하나 없이 깨끗하다.",
                "DIRTY": "낙엽이 마르고 삭아 벤치 표면에 달라붙어 있다.",
                "WET": "최근 비에 젖어 축축하고 무거운 기운을 풍긴다."
            }
        )
        self.object_list.append(wood_bench)

        return self.object_list
    
    