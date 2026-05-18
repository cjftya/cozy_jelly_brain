from sim.object_meta.space_object import SpaceObject
from sim.object_meta.building_object import BuildingObject
from sim.object_meta.item_object import ItemObject

class WorldObjectCreator:
    def __init__(self):
        pass

    def create_lim_world(self):
        objects = []

        # LIM의 집
        lim_house = BuildingObject(
            name="LIM의 집",
            detail="주변에 아무도 없고 어둡고 음산한 기운이 도는 집."
        )
        objects.append(lim_house)

        objects.append(SpaceObject("자는방", "어두운 침실, 따로 가구는 없고 침대만 덩그러니 있다.", lim_house))
        objects.append(ItemObject("거울", "자신의 얼굴을 비추는 거울", sleeping_room))
        objects.append(ItemObject("침대", "잠을 잘 수 있는 침대, 하지만 누군가 지켜보는 듯한 기분이 든다.", sleeping_room))

        objects.append(SpaceObject("거실", "비교적 깔끔한 거실, 어딘가 서늘한 기운이 감돈다", lim_house))
        objects.append(ItemObject("쇼파", "누군가 앉았던 흔적이 있는 쇼파", living_room))
        objects.append(ItemObject("가족사진", "행복했던 날의 추억이 담긴 가족사진", living_room))
        objects.append(ItemObject("TV", "큰 대형TV, 한번도 켜진 적 없는 듯 먼지가 쌓여있다", living_room))

        # 성당
        church = BuildingObject(
            name="성당",
            detail="성스러운 기운이 느껴지는 고요한 성당. 십자가와 제단이 중앙에 있다."
        )
        objects.append(church)

        objects.append(SpaceObject("기도실", "제단이 있는 기도실. 성스러운 기운이 감도는 공간이다.", church))
        objects.append(ItemObject("예수님상", "제단에 서 있는 예수님상", prayer_room))
        objects.append(ItemObject("의자", "성당앞에 서 있는 의자들", prayer_room))
        
        objects.append(SpaceObject("조각상 정원", "성당 바깥쪽에 있는 조각상 정원. 성모마리아상이 가운데 서 있다.", church))
        objects.append(ItemObject("성모마리아상", "정원 가운데 서 있는 성모마리아상", garden))

        return objects