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

    def remove_object(self, id):
        if id in self.objects:
            self.objects.pop(id)

    def clear_objects(self):
        self.objects.clear()

    def get_object_context(self, id):
        obj = self.get_object(id)
        if obj:
            return f"- **{obj.name}** (id: {obj.id}) - (detail: {obj.detail})"
        return ""

    def get_objects_full_context(self):
        if not self.objects:
            return "관찰된 대상 없음"
            
        description_list = []
        for obj in self.objects.values():
            description_list.append(self.get_object_context(obj.id))
        return "\n".join(description_list)