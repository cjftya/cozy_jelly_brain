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

    def remove_object(self, id):
        if id in self.objects:
            self.objects.pop(id)