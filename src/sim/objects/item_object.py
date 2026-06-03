from sim.objects.base_object import BaseObject
from sim.object_meta.object_type import ObjectType, ObjectDetailType

class ItemObject(BaseObject):
    def __init__(self, name, detail=None, detail_type=ObjectDetailType.DEFAULT_ITEM, parent=None):
        super().__init__(name, detail, detail_type, ObjectType.ITEM, parent)

        # 상태 속성
        self.state_map = {}
        self.current_state = None
        self.nutrition_value = 0

    def use(self):
        return self.detail_type, False

    def set_nutri(self, nutrition_value):
        self.nutrition_value = nutrition_value

    def set_state(self, state, state_detail):
        self.current_state = state
        self.state_map[state] = state_detail

    def get_current_state(self):
        return self.current_state