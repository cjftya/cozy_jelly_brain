from sim.util.point import Point
from sim.object_meta.object_type import ObjectType
from sim.object_meta.object_manager import ObjectManager
from sim.util.globar_util import GlobarUtil

class BaseObject:
    def __init__(self, name=None, detail=None, obj_type=None, parent=None):
        self.id = GlobarUtil.gen_object_id()
        self.name = name
        self.detail = detail
        self.type = obj_type
        self.parent = parent

        # 좌표
        self.position = Point()

        # 물리 속성
        self.size = Point()
        self.weight = 0

        # 기능적 속성
        self.is_interactive = False

        # 위치 속성
        self.location = None

    def set_name(self, name):
        self.name = name

    def set_type(self, obj_type):
        self.type = obj_type

    def set_detail(self, detail):
        self.detail = detail

    def set_interactive(self, interactive):
        self.is_interactive = interactive

    def set_location(self, location):
        self.location = location

    def set_size(self, w, h):
        self.size.x = w
        self.size.y = h

    def set_weight(self, weight):
        self.weight = weight