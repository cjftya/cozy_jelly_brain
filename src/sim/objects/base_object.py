from sim.objects.atomic_object import AtomicObject
from sim.object_meta.object_type import ObjectDetailType
from sim.util.point import Point
from sim.util.object_manager import ObjectManager
from sim.util.global_util import GlobalUtil

class BaseObject(AtomicObject):
    def __init__(self, name=None, state=None, detail=None, detail_type=None, obj_type=None, parent=None):
        super().__init__(name, GlobalUtil.gen_object_id(), parent)
        self.state = state
        self.detail = detail
        self.detail_type = detail_type
        self.type = obj_type

        # 좌표
        self.position = Point()

        # 물리 속성
        self.size = Point()
        self.weight = 0

    def set_name(self, name):
        self.name = name

    def set_type(self, obj_type):
        self.type = obj_type

    def set_detail(self, detail):
        self.detail = detail

    def get_detail(self):
        return self.detail

    def set_detail_type(self, detail_type):
        self.detail_type = detail_type

    def set_pos(self, x, y):
        self.position.set_value(x, y)

    def set_size(self, w, h):
        self.size.set_value(w, h)

    def set_weight(self, weight):
        self.weight = weight

    def set_state(self, state, detail):
        self.state = state
        self.detail = detail