from sim.util.point import Point
from sim.util.object_manager import ObjectManager
from sim.object_meta.object_type import ObjectDetailType
from sim.util.global_util import GlobalUtil

class BaseObject:
    def __init__(self, name=None, detail=None, detail_type=None, obj_type=None, parent=None):
        self.id = GlobalUtil.gen_object_id()
        self.name = name
        self.detail = detail
        self.detail_type = detail_type
        self.type = obj_type
        self.parent = parent

        # 좌표
        self.position = Point()

        # 물리 속성
        self.size = Point()
        self.weight = 0

    def use(self):
        return self.detail_type, False

    def set_name(self, name):
        self.name = name

    def set_type(self, obj_type):
        self.type = obj_type

    def set_detail(self, detail):
        self.detail = detail

    def set_detail_type(self, detail_type):
        self.detail_type = detail_type

    def set_pos(self, x, y):
        self.position.set_value(x, y)

    def set_size(self, w, h):
        self.size.set_value(w, h)

    def set_weight(self, weight):
        self.weight = weight