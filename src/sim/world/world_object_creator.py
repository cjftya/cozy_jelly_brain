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

        objects.append(SpaceObject(name="자는방", detail="어두운 침실, 따로 가구는 없고 침대만 덩그러니 있다."))
        objects.append(ItemObject(name="거울", detail="자신의 얼굴을 비추는 거울"))
        objects.append(ItemObject(name="침대", detail="잠을 잘 수 있는 침대, 하지만 누군가 지켜보는 듯한 기분이 든다."))

        objects.append(SpaceObject(name="거실", detail="비교적 깔끔한 거실, 어딘가 서늘한 기운이 감돈다"))
        objects.append(ItemObject(name="쇼파", detail="누군가 앉았던 흔적이 있는 쇼파"))
        objects.append(ItemObject(name="가족사진", detail="행복했던 날의 추억이 담긴 가족사진"))
        objects.append(ItemObject(name="TV", detail="큰 대형TV, 한번도 켜진 적 없는 듯 먼지가 쌓여있다"))

        # 성당
        church = BuildingObject(
            name="성당",
            detail="성스러운 기운이 느껴지는 고요한 성당. 십자가와 제단이 중앙에 있다."
        )
        objects.append(church)

        objects.append(SpaceObject(name="기도실", detail="제단이 있는 기도실. 성스러운 기운이 감도는 공간이다."))
        objects.append(ItemObject(name="예수님상", detail="제단에 서 있는 예수님상"))
        objects.append(ItemObject(name="의자", detail="성당앞에 서 있는 의자들"))
        
        objects.append(SpaceObject(name="조각상 정원", detail="성당 바깥쪽에 있는 조각상 정원. 성모마리아상이 가운데 서 있다."))
        objects.append(ItemObject(name="성모마리아상", detail="정원 가운데 서 있는 성모마리아상"))

        return objects