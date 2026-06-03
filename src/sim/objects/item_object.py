from sim.objects.base_object import BaseObject
from sim.object_meta.object_type import ObjectType, ObjectDetailType

class ItemObject(BaseObject):
    def __init__(self, name, state=None, detail=None, detail_type=ObjectDetailType.DEFAULT_ITEM, parent=None):
        super().__init__(name, state, detail, detail_type, ObjectType.ITEM, parent)

        # 상태 속성
        self.nutrition_value = 0

    def set_nutri(self, nutrition_value):
        self.nutrition_value = nutrition_value

    def set_state(self, state, detail):
        self.state = state
        self.detail = detail