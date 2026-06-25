import threading

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
        self._lock = threading.RLock()

    def get_objects_by_name(self, name):
        """지정된 이름을 가진 모든 객체 리스트(그룹)를 반환합니다."""
        with self._lock:
            return self.objects.get(name, [])

    def get_object(self, name):
        """지정된 이름을 가진 객체 중 첫 번째 객체를 반환합니다."""
        with self._lock:
            group = self.objects.get(name)
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

        with self._lock:
            str_id = str(id).strip()
            str_id_upper = str_id.upper()
            prefixed_id_upper = f"OBJECT_{str_id}".upper() if str_id.isdigit() else None

            # 1~2단계: 활성 객체 ID 매칭 (Exact, Case-Insensitive, Prefixed ID 순서로 우선순위 부여)
            best_match = None
            match_priority = 99  # 낮은 값일수록 우선순위가 높음

            for group in self.objects.values():
                for obj in group:
                    obj_id = getattr(obj, "id", "")
                    if not obj_id:
                        continue

                    obj_id_upper = obj_id.upper()
                    if obj_id == id:
                        return obj  # 가장 우선순위가 높은 Exact Match이므로 즉시 반환
                    elif obj_id_upper == str_id_upper:
                        if match_priority > 2:
                            best_match = obj
                            match_priority = 2
                    elif prefixed_id_upper and obj_id_upper == prefixed_id_upper:
                        if match_priority > 3:
                            best_match = obj
                            match_priority = 3

            if best_match:
                return best_match

            # 3단계: 이름 매칭 백업 (LLM이 ID 대신 사물 이름을 그대로 전달한 경우)
            group = self.objects.get(str_id)
            if group:
                return group[0]

            # 4단계: 이미 삭제(pop)된 객체 ID에 대한 동일 이름의 다른 활성 객체 대체 매칭 (Fallback)
            popped_name = None
            if id in self.popped_metadata:
                popped_name = self.popped_metadata[id].get("name")
            else:
                # 대소문자 및 접두사 보정 매칭을 적용하여 삭제 기록 검색
                for popped_id, meta in self.popped_metadata.items():
                    popped_id_upper = str(popped_id).upper()
                    if popped_id_upper == str_id_upper or (
                        prefixed_id_upper and popped_id_upper == prefixed_id_upper
                    ):
                        popped_name = meta.get("name")
                        break

            if popped_name:
                fallback_group = self.objects.get(popped_name)
                if fallback_group:
                    return fallback_group[0]

        return None

    def get_objects(self):
        """관리 중인 모든 객체를 단일 1차원 리스트로 반환합니다."""
        with self._lock:
            return [obj for lst in self.objects.values() for obj in lst]

    def get_objects_by_type(self, obj_type):
        """특정 타입(예: ITEM, SPACE, BUILDING)에 해당하는 모든 객체 리스트를 반환합니다."""
        with self._lock:
            return [
                obj
                for group in self.objects.values()
                for obj in group
                if obj.type == obj_type
            ]

    def get_objects_by_parent_name(self, parent_name):
        """특정 부모 공간에 배치된 모든 객체 리스트를 반환합니다."""
        with self._lock:
            return [
                obj
                for group in self.objects.values()
                for obj in group
                if obj.parent and getattr(obj.parent, "name", None) == parent_name
            ]

    def has_object(self, name):
        """지정된 이름을 가진 객체 그룹이 관리 테이블에 존재하는지 확인합니다."""
        with self._lock:
            return name in self.objects

    def add_object(self, obj):
        """객체를 추가합니다. 동일한 이름의 객체가 있다면 리스트(그룹)에 누적되어 관리됩니다."""
        if obj and getattr(obj, "name", None):
            with self._lock:
                self.objects.setdefault(obj.name, []).append(obj)

    def add_objects(self, objs):
        """여러 개의 객체들을 순차적으로 추가합니다."""
        for obj in objs:
            self.add_object(obj)

    def pop_object(self, name):
        """지정된 이름을 가진 객체 중 첫 번째 객체를 제거하고 반환합니다. 삭제 메타데이터에 기록됩니다."""
        with self._lock:
            group = self.objects.get(name)
            if group:
                obj = group.pop(0)
                if not group:
                    self.objects.pop(name, None)
                self.popped_metadata[obj.id] = {"name": obj.name}
                return obj
            return None

    def pop_object_by_id(self, id):
        """특정 ID를 가진 객체를 찾아 제거하고 반환합니다. 삭제 메타데이터에 기록됩니다."""
        with self._lock:
            obj = self.get_object_by_id(id)
            if obj:
                group = self.objects.get(obj.name)
                if group and obj in group:
                    group.remove(obj)
                    if not group:
                        self.objects.pop(obj.name, None)
                    self.popped_metadata[obj.id] = {"name": obj.name}
                    return obj
            return None

    def pop_objects_by_name(self, name):
        """지정된 이름을 가진 모든 객체 리스트(그룹)를 통째로 제거하고 반환합니다."""
        with self._lock:
            return self.objects.pop(name, None)

    def clear_objects(self):
        """관리 테이블의 모든 객체 정보와 삭제 이력 메타데이터를 제거합니다."""
        with self._lock:
            self.objects.clear()
            self.popped_metadata.clear()

    def get_group_context(self, group):
        """
        동일한 이름을 가진 객체 그룹의 검사 여부(is_inspected)별 수량을 분류/요약하여
        LLM 인지에 최적화된 텍스트 컨텍스트로 컴파일하여 반환합니다.
        (예: 검사 완료된 아이템(상세 표기 포함)과 그렇지 않은 아이템을 구분하여 표시)
        """
        if not group:
            return ""

        obj = group[0]
        if obj.type != ObjectType.ITEM:
            return f"- [name: {obj.name}] - [object_id: {obj.id}]"

        # 아이템 타입인 경우 동일 이름 내에서도 검사 여부(is_inspected)별로 세분화하여 그룹화
        groups = {}
        for o in group:
            groups.setdefault(getattr(o, "is_inspected", False), []).append(o)

        lines = []
        for is_inspected_val, items in groups.items():
            representative = items[0]
            detail_str = ""
            if is_inspected_val and getattr(representative, "detail", None):
                detail_str = (
                    f" - [detail: {representative.detail}] - (already inspected)"
                )
            lines.append(
                f"- [name: {representative.name}] - [object_id: {representative.id}] - [count: {len(items)}]{detail_str}"
            )
        return "\n".join(lines)

    def get_objects_full_context(self):
        """
        관리 테이블에 존재하는 모든 객체들의 상세 상태 및 그룹화된 컨텍스트를
        줄바꿈으로 병합하여 프롬프트 주입용 전체 요약 텍스트를 생성합니다.
        """
        with self._lock:
            if not self.objects:
                return "관찰된 대상 없음"

            description_list = [
                self.get_group_context(group) for group in self.objects.values()
            ]
            return "\n".join(filter(None, description_list))
