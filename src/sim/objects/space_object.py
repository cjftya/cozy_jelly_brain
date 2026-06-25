from sim.object_meta.object_type import ObjectDetailType, ObjectType
from sim.objects.base_object import BaseObject


class SpaceObject(BaseObject):
    def __init__(
        self, name, detail=None, detail_type=ObjectDetailType.DEFAULT_SPACE, parent=None
    ):
        super().__init__(name, detail, detail_type, ObjectType.SPACE, parent)
