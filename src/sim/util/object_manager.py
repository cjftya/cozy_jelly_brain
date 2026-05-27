from sim.object_meta.object_type import ObjectType

class ObjectManager:
    def __init__(self):
        # key: object_id, value: queue
        self.objects = {}

    def get_pack(self, name):
        # 오브젝트의 큐 전체 반환
        return self.objects.get(name, [])

    def get_object(self, name):
        # 오브젝트 하나 리턴
        return self.get_pack(name)[0] if self.get_pack(name) else None

    def get_object_by_id(self, id):
        # 특정 id로 오브젝트 반환
        for pack in self.objects.values():
            for obj in pack:
                if obj.id == id:
                    return obj
        return None

    def get_objects(self):
        # 전체 오브젝트 리스트 반환
        return [obj for lst in self.objects.values() for obj in lst]

    def get_objects_by_type(self, obj_type):
        # 특정 타입으로 오브젝트 리스트 반환
        result = []
        for pack in self.objects.values():
            for obj in pack:
                if obj.type == obj_type:
                    result.append(obj)
        return result

    def get_objects_by_parent(self, parent):
        # 특정 부모를 가진 오브젝트 리스트 반환
        result = []
        parent_id = parent.id
        for pack in self.objects.values():
            for obj in pack:
                if obj.parent and obj.parent.id == parent_id:
                    result.append(obj)
        return result

    def get_childs_by_parent(self, parent):
        # 부모 오브젝트를 가진 자식 오브젝트 리스트 반환
        result = []
        parent_id = parent.id
        for obj_list in self.objects.values():
            for obj in obj_list:
                if obj.parent and obj.parent.id == parent_id:
                    result.append(obj)
        return result

    def has_object(self, name):
        # 오브젝트가 큐에 있는지 확인
        return name in self.objects

    def add_object(self, obj):
        # 오브젝트를 큐에 추가
        pack = self.get_pack(obj.name)
        if not pack:
            self.objects[obj.name] = [obj]
        else:
            pack.append(obj)

    def add_objects(self, objs):
        # 오브젝트들을 큐에 추가
        for obj in objs:
            self.add_object(obj)

    def pop_object(self, name):
        # 오브젝트 큐에서 하나 제거 후 반환
        pack = self.get_pack(name)
        if pack:
            obj = pack.pop(0)
            if len(pack) == 0:
                self.objects.pop(name, None)
            return obj
        return None

    def pop_pack(self, name):
        # 오브젝트 큐에서 팩 제거 후 반환
        return self.objects.pop(name, None)

    def clear_objects(self):
        # 모든 오브젝트 제거
        self.objects.clear()

    def get_object_context(self, pack):
        obj = pack[0] if pack else None
        if obj:
            description = ""
            if obj.type == ObjectType.ITEM:
                state, detail = obj.get_current_state()
                count = len(pack)
                description = detail if detail is not None else obj.detail
                return f"- [name: {obj.name}] - [object_id: {obj.id}] - [count: {count}] - [detail: {description}]"
            else:
                description = obj.detail

            return f"- [name: {obj.name}] - [object_id: {obj.id}] - [detail: {description}]"
        return ""

    def get_objects_full_context(self):
        if not self.objects:
            return "관찰된 대상 없음"

        description_list = []
        for obj_name in self.objects.keys():
            description_list.append(self.get_object_context(self.get_pack(obj_name)))
        return "\n".join(description_list)