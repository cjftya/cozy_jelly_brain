from sim.object_meta.object_type import ObjectType

class ObjectManager:
    def __init__(self):
        self.objects = {}

    def get_object(self, id):
        return self.objects.get(id)

    def get_objects_by_type(self, obj_type):
        return [obj for obj in self.objects.values() if obj.type == obj_type]

    def get_objects(self, obj_type=None):
        if obj_type is None:
            return list(self.objects.values())
        return self.get_objects_by_type(obj_type)

    def add_object(self, obj):
        self.objects[obj.id] = obj

    def add_objects(self, objs):
        for obj in objs:
            self.add_object(obj)

    def remove_object(self, obj):
        if obj.id in self.objects:
            self.objects.pop(obj.id)

    def clear_objects(self):
        self.objects.clear()

    def get_object_context(self, id):
        obj = self.get_object(id)
        if obj:
            description = ""
            if obj.type == ObjectType.ITEM:
                state, detail = obj.get_current_state()
                description = detail if detail is not None else obj.detail
            else:
                description = obj.detail

            return f"- [name: {obj.name}] - [object_id: {obj.id}] - [detail: {description}]"
        return ""

    def get_objects_full_context(self):
        if not self.objects:
            return "관찰된 대상 없음"
            
        description_list = []
        for obj in self.objects.values():
            description_list.append(self.get_object_context(obj.id))
        return "\n".join(description_list)

    def find_space(self, name):
        for obj in self.objects.values():
            if obj.name == name and obj.type == ObjectType.SPACE:
                return obj
        return None

    def find_item(self, name, parent_name=None):
        for obj in self.objects.values():
            if obj.name == name and obj.type == ObjectType.ITEM:
                if parent_name is None:
                    return obj
                elif obj.parent and obj.parent.name == parent_name:
                    return obj
        return None

    def find_building(self, name):
        for obj in self.objects.values():
            if obj.name == name and obj.type == ObjectType.BUILDING:
                return obj
        return None

    def find_childs(self, parent):
        result = []
        for obj in self.objects.values():
            if obj.parent and obj.parent.id == parent.id:
                result.append(obj)
        return result

    def has_object(self, obj):
        for o in self.objects.values():
            if o.id == obj.id:
                return True
        return False