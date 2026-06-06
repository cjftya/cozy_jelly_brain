from sim.object_meta.object_type import ObjectType

class ObjectManager:
    def __init__(self):
        # key: object_name (str), value: list of objects (list)
        self.objects = {}
        # key: object_id (str), value: dict of metadata
        self.popped_metadata = {}

    def get_pack(self, name):
        # 오브젝트의 큐 전체 반환
        return self.objects.get(name, [])

    def get_object(self, name):
        # 오브젝트 하나 리턴
        pack = self.get_pack(name)
        return pack[0] if pack else None

    def get_object_by_id(self, id):
        if id is None:
            return None

        # 1단계: 정밀 일치 (Exact Match)
        for pack in self.objects.values():
            for obj in pack:
                if obj.id == id:
                    return obj

        # 2단계: 타입 변환 및 정규화 (int -> str, 대소문자 무시, 접두사 보정)
        # 예: 5 -> "5" -> "OBJECT_5"
        str_id = str(id).strip()
        
        # 대소문자 무시 비교
        for pack in self.objects.values():
            for obj in pack:
                if obj.id.upper() == str_id.upper():
                    return obj

        # 숫자만 넘어온 경우 보정 (예: 5 또는 "5" -> "OBJECT_5")
        target_prefixed_id = None
        if str_id.isdigit():
            target_prefixed_id = f"OBJECT_{str_id}"
            for pack in self.objects.values():
                for obj in pack:
                    if obj.id.upper() == target_prefixed_id.upper():
                        return obj

        # 3단계: 이름 매칭 백업
        # LLM이 ID 대신 사물 이름을 그대로 보낸 경우 처리
        # 해당 이름의 팩이 존재하면 첫 번째 객체를 반환
        pack = self.get_pack(str_id)
        if pack:
            return pack[0]

        # 4단계: 이미 삭제(pop)된 객체 ID에 대한 동일 이름의 다른 활성 객체 대체 매칭 (Fallback)
        # 예: OBJECT_3가 이미 수집되었으나, 같은 이름("과일")의 다른 객체가 여전히 맵에 존재하는 경우
        if id in self.popped_metadata:
            meta = self.popped_metadata[id]
            name = meta.get("name")
            if name:
                fallback_pack = self.get_pack(name)
                if fallback_pack:
                    return fallback_pack[0]

        # 정규화된 ID로도 popped_metadata 조회 시도
        norm_id = target_prefixed_id if target_prefixed_id else str_id
        for popped_id, meta in list(self.popped_metadata.items()):
            if popped_id.upper() == norm_id.upper():
                name = meta.get("name")
                if name:
                    fallback_pack = self.get_pack(name)
                    if fallback_pack:
                        return fallback_pack[0]

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

    def get_objects_by_parent_name(self, parent_name):
        # 특정 부모이름을 가진 오브젝트 리스트 반환
        result = []
        for pack in self.objects.values():
            for obj in pack:
                if obj.parent and getattr(obj.parent, 'name', None) == parent_name:
                    result.append(obj)
        return result

    def has_object(self, name):
        # 오브젝트가 큐에 있는지 확인
        return name in self.objects

    def add_object(self, obj):
        # 오브젝트를 큐에 추가
        if obj and getattr(obj, 'name', None):
            self.objects.setdefault(obj.name, []).append(obj)

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
            if obj:
                self.popped_metadata[obj.id] = {"name": obj.name}
            return obj
        return None

    def pop_object_by_id(self, id):
        # 특정 id로 오브젝트를 제거 후 반환
        obj = self.get_object_by_id(id)
        if obj:
            pack = self.get_pack(obj.name)
            if pack and obj in pack:
                pack.remove(obj)
                if len(pack) == 0:
                    self.objects.pop(obj.name, None)
                self.popped_metadata[obj.id] = {"name": obj.name}
                return obj
        return None

    def pop_pack(self, name):
        # 오브젝트 큐에서 팩 제거 후 반환
        return self.objects.pop(name, None)

    def clear_objects(self):
        # 모든 오브젝트 제거
        self.objects.clear()
        self.popped_metadata.clear()

    def get_object_context(self, pack):
        if not pack:
            return ""
        
        obj = pack[0]
        # 아이템인 경우 동일 이름 내에서도 상태(state)별로 그룹화하여 컨텍스트에 표시
        if obj.type == ObjectType.ITEM:
            state_groups = {}
            for o in pack:
                state_groups.setdefault(o.state or "기본", []).append(o)
            
            lines = []
            for state_val, items in state_groups.items():
                count = len(items)
                representative = items[0]
                state_str = f" - [state: {state_val}]" if representative.state else ""
                description = representative.detail or ""
                lines.append(f"- [name: {representative.name}] - [object_id: {representative.id}] - [count: {count}]{state_str} - [detail: {description}]")
            return "\n".join(lines)
        else:
            description = obj.detail or ""
            return f"- [name: {obj.name}] - [object_id: {obj.id}] - [detail: {description}]"

    def get_objects_full_context(self):
        if not self.objects:
            return "관찰된 대상 없음"

        description_list = []
        for obj_name in self.objects.keys():
            context = self.get_object_context(self.get_pack(obj_name))
            if context:
                description_list.append(context)
        return "\n".join(description_list)