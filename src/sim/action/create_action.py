from sim.action.base_action import BaseAction
from sim.objects.item_object import ItemObject
from sim.objects.building_object import BuildingObject
from sim.objects.space_object import SpaceObject
from sim.object_meta.object_type import ObjectType

class CreateAction(BaseAction):
    def __init__(self, world_system_manager):
        super().__init__(world_system_manager)

    def execute(self, *args):
        # args: created_name, location_name, pos_x, pos_y, created_object_type
        if len(args) < 4:
            self.world_system_manager.log_system_event("skip function call: create, args insufficient")
            return

        created_name = args[0]
        location_name = args[1]
        pos_x = float(args[2])
        pos_y = float(args[3])
        created_object_type = int(args[4]) if len(args) > 4 else ObjectType.ITEM

        # 생성될 방(부모) 찾기
        parent_space = self.world_system_manager.object_manager.get_object(location_name)
        
        # LLM이 정해준 타입에 따라 정확한 클래스 인스턴스 생성
        if created_object_type == ObjectType.SPACE:
            new_obj = SpaceObject(name=created_name, detail=f"새롭게 개척/구축된 {created_name} 공간입니다.", parent=parent_space)
            new_obj.set_size(10, 10) # 공간일 경우 임의의 넓이 부여
            
        elif created_object_type == ObjectType.BUILDING:
            new_obj = BuildingObject(name=created_name, detail=f"새롭게 건설된 {created_name} 구조물입니다.", parent=parent_space)
            
        else: # 기본값 ITEM
            new_obj = ItemObject(name=created_name, detail=f"방금 조합된 {created_name}입니다.", parent=parent_space)
        
        # 좌표 세팅 및 월드 영구 등록
        new_obj.set_pos(pos_x + 1.0, pos_y) 
        self.world_system_manager.object_manager.add_object(new_obj)