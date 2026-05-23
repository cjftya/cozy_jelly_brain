from sim.objects.base_object import BaseObject
from sim.object_meta.object_type import ObjectType, ObjectDetailType

class ItemObject(BaseObject):
    def __init__(self, name, detail=None, detail_type=ObjectDetailType.DEFAULT_ITEM, parent=None):
        super().__init__(name, detail, detail_type, ObjectType.ITEM, parent)
        self.is_interactive = True

        # 상태 속성
        self.states = []
        self.state_details = {}
        self.current_state_idx = 0

    def use(self):
        if self.detail_type in [ObjectDetailType.FOOD, ObjectDetailType.DRINK]:
            return self.detail_type, True

        if self.states:
            self.current_state_idx = (self.current_state_idx + 1) % len(self.states)
            return self.detail_type, False

        return self.detail_type, False

    def set_state_machine(self, states, state_details):
        """사물의 가용 상태 흐름과 상태별 세부 묘사를 정의합니다."""
        self.states = states
        self.state_details = state_details
        self.current_state_idx = 0

    def get_current_state(self):
        if self.states and self.state_details:
            state_name = self.states[self.current_state_idx]
            return state_name, self.state_details[state_name]
        return None, None