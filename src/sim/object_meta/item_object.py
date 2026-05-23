from sim.object_meta.base_object import BaseObject
from sim.object_meta.object_type import ObjectType, ObjectDetailType

class ItemObject(BaseObject):
    def __init__(self, name, detail=None, detail_type=ObjectDetailType.DEFAULT_ITEM, parent=None):
        super().__init__(name, detail, detail_type, ObjectType.ITEM, parent)
        self.is_interactive = True

    def use(self):
        if self.detail_type == ObjectDetailType.FOOD:
            return self.detail_type, True
        elif self.detail_type == ObjectDetailType.DRINK:
            return self.detail_type, True
        else:
            return self.detail_type, False