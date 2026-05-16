from sim.object_meta.base_object import BaseObject
from sim.object_meta.object_type import ObjectType

class ItemObject(BaseObject):
    def __init__(self, id):
        super().__init__(id, ObjectType.ITEM)