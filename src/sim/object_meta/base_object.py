from sim.util.point import Point
from sim.object_meta.object_type import ObjectType
from sim.object_meta.object_manager import ObjectManager
from sim.util.globar_util import GlobarUtil

class BaseObject:
    def __init__(self, name, obj_type):
        self.id = GlobarUtil.gen_object_id()
        self.type = obj_type

        # 좌표
        self.position = Point()

        # 소유 속성
        self.owner_id = None

        # 일반 속성
        self.name = ""
        self.description = ""
        
        # 물리 속성
        self.color = ""
        self.size = Point()
        self.weight = 0

        # 기능적 속성
        self.is_breakable = False
        self.is_interactive = False

        # 위치 속성
        self.location = None

        # 자식 객체 관리
        self.child_objects = ObjectManager()