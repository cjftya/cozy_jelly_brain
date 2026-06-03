from sim.objects.base_object import BaseObject
from sim.object_meta.object_type import ObjectType, ObjectDetailType

class BuildingObject(BaseObject):
    def __init__(self, name, state=None, detail=None, detail_type=ObjectDetailType.DEFAULT_BUILDING, parent=None):
        super().__init__(name, state, detail, detail_type, ObjectType.BUILDING, parent)