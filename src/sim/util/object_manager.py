from sim.object_meta.object_type import ObjectType

class ObjectManager:
    """
    월드 내의 모든 객체(아이템, 공간 등)들을 관리하는 매니저 클래스입니다.
    객체의 추가, 삭제, ID 및 이름 기반 검색, 그리고 LLM 프롬프트 주입을 위한 
    컨텍스트 생성을 담당합니다.
    """
    def __init__(self):
        # key: 객체 이름 (str), value: 객체 리스트 (list) - 동일 이름의 객체들을 그룹으로 관리합니다.
        self.objects = {}
        # key: 삭제된 객체 ID (str), value: 객체 메타데이터 (dict) - 수집/삭제 후 대체 매칭용 히스토리 추적 정보입니다.
        self.popped_metadata = {}

    def get_objects_by_name(self, name):
        """지정된 이름을 가진 모든 객체 리스트(그룹)를 반환합니다."""
        return self.objects.get(name, [])

    def get_object(self, name):
        """지정된 이름을 가진 객체 중 첫 번째 객체를 반환합니다."""
        group = self.get_objects_by_name(name)
        return group[0] if group else None

    def get_object_by_id(self, id):
        """
        객체의 고유 ID를 기반으로 검색합니다.
        대소문자 무시 매칭, 정수형 ID 보정, 이름 백업 매칭, 그리고 이미 삭제된
        아이템 ID 요청 시 동일한 이름의 다른 활성 객체로 자동 우회 매칭(Popped Fallback)하는 
        4단계의 견고한 탐색 알고리즘을 지원합니다.
        """
        if id is None:
            return None

        # 1단계: 정밀 일치 (Exact Match)
        for group in self.objects.values():
            for obj in group:
                if obj.id == id:
                    return obj

        # 2단계: 타입 변환 및 정규화 (int -> str, 대소문자 무시, 접두사 보정)
        # 예: 5 -> "5" -> "OBJECT_5"
        str_id = str(id).strip()
        
        # 대소문자 무시 비교
        for group in self.objects.values():
            for obj in group:
                if obj.id.upper() == str_id.upper():
                    return obj

        # 숫자만 넘어온 경우 보정 (예: 5 또는 "5" -> "OBJECT_5")
        target_prefixed_id = None
        if str_id.isdigit():
            target_prefixed_id = f"OBJECT_{str_id}"
            for group in self.objects.values():
                for obj in group:
                    if obj.id.upper() == target_prefixed_id.upper():
                        return obj

        # 3단계: 이름 매칭 백업
        # LLM이 ID 대신 사물 이름을 그대로 보낸 경우 처리
        # 해당 이름의 그룹이 존재하면 첫 번째 객체를 반환
        group = self.get_objects_by_name(str_id)
        if group:
            return group[0]

        # 4단계: 이미 삭제(pop)된 객체 ID에 대한 동일 이름의 다른 활성 객체 대체 매칭 (Fallback)
        # 예: OBJECT_3가 이미 수집되었으나, 같은 이름("과일")의 다른 객체가 여전히 맵에 존재하는 경우
        if id in self.popped_metadata:
            meta = self.popped_metadata[id]
            name = meta.get("name")
            if name:
                fallback_group = self.get_objects_by_name(name)
                if fallback_group:
                    return fallback_group[0]

        # 정규화된 ID로도 popped_metadata 조회 시도
        norm_id = target_prefixed_id if target_prefixed_id else str_id
        for popped_id, meta in list(self.popped_metadata.items()):
            if popped_id.upper() == norm_id.upper():
                name = meta.get("name")
                if name:
                    fallback_group = self.get_objects_by_name(name)
                    if fallback_group:
                        return fallback_group[0]

        return None

    def get_objects(self):
        """관리 중인 모든 객체를 단일 1차원 리스트로 반환합니다."""
        return [obj for lst in self.objects.values() for obj in lst]

    def get_objects_by_type(self, obj_type):
        """특정 타입(예: ITEM, SPACE, BUILDING)에 해당하는 모든 객체 리스트를 반환합니다."""
        result = []
        for group in self.objects.values():
            for obj in group:
                if obj.type == obj_type:
                    result.append(obj)
        return result

    def get_objects_by_parent_name(self, parent_name):
        """특정 부모 공간에 배치된 모든 객체 리스트를 반환합니다."""
        result = []
        for group in self.objects.values():
            for obj in group:
                if obj.parent and getattr(obj.parent, 'name', None) == parent_name:
                    result.append(obj)
        return result

    def has_object(self, name):
        """지정된 이름을 가진 객체 그룹이 관리 테이블에 존재하는지 확인합니다."""
        return name in self.objects

    def add_object(self, obj):
        """객체를 추가합니다. 동일한 이름의 객체가 있다면 리스트(그룹)에 누적되어 관리됩니다."""
        if obj and getattr(obj, 'name', None):
            self.objects.setdefault(obj.name, []).append(obj)

    def add_objects(self, objs):
        """여러 개의 객체들을 순차적으로 추가합니다."""
        for obj in objs:
            self.add_object(obj)

    def pop_object(self, name):
        """지정된 이름을 가진 객체 중 첫 번째 객체를 제거하고 반환합니다. 삭제 메타데이터에 기록됩니다."""
        group = self.get_objects_by_name(name)
        if group:
            obj = group.pop(0)
            if len(group) == 0:
                self.objects.pop(name, None)
            if obj:
                self.popped_metadata[obj.id] = {"name": obj.name}
            return obj
        return None

    def pop_object_by_id(self, id):
        """특정 ID를 가진 객체를 찾아 제거하고 반환합니다. 삭제 메타데이터에 기록됩니다."""
        obj = self.get_object_by_id(id)
        if obj:
            group = self.get_objects_by_name(obj.name)
            if group and obj in group:
                group.remove(obj)
                if len(group) == 0:
                    self.objects.pop(obj.name, None)
                self.popped_metadata[obj.id] = {"name": obj.name}
                return obj
        return None

    def pop_objects_by_name(self, name):
        """지정된 이름을 가진 모든 객체 리스트(그룹)를 통째로 제거하고 반환합니다."""
        return self.objects.pop(name, None)

    def clear_objects(self):
        """관리 테이블의 모든 객체 정보와 삭제 이력 메타데이터를 제거합니다."""
        self.objects.clear()
        self.popped_metadata.clear()

    def get_group_context(self, group):
        """
        동일한 이름을 가진 객체 그룹의 상태(State)별 수량을 분류/요약하여
        LLM 인지에 최적화된 텍스트 컨텍스트로 컴파일하여 반환합니다.
        (예: 젖은 상태의 아이템 2개와 마른 상태의 아이템 1개를 그룹화하여 표시)
        """
        if not group:
            return ""
        
        obj = group[0]
        # 아이템 타입인 경우 동일 이름 내에서도 상태(state)별로 세분화하여 그룹화
        if obj.type == ObjectType.ITEM:
            state_groups = {}
            for o in group:
                state_groups.setdefault(o.state or "기본", []).append(o)
            
            lines = []
            for state_val, items in state_groups.items():
                count = len(items)
                representative = items[0]
                state_str = f" - [state: {state_val}]" if representative.state else ""
                lines.append(f"- [name: {representative.name}] - [object_id: {representative.id}] - [count: {count}]{state_str}")
            return "\n".join(lines)
        else:
            return f"- [name: {obj.name}] - [object_id: {obj.id}]"

    def get_objects_full_context(self):
        """
        관리 테이블에 존재하는 모든 객체들의 상세 상태 및 그룹화된 컨텍스트를
        줄바꿈으로 병합하여 프롬프트 주입용 전체 요약 텍스트를 생성합니다.
        """
        if not self.objects:
            return "관찰된 대상 없음"

        description_list = []
        for obj_name in self.objects.keys():
            context = self.get_group_context(self.get_objects_by_name(obj_name))
            if context:
                description_list.append(context)
        return "\n".join(description_list)