from sim.objects.base_object import BaseObject
from sim.object_meta.object_type import ObjectType, ObjectDetailType

class ItemObject(BaseObject):
    def __init__(self, name, state=None, detail=None, detail_type=ObjectDetailType.DEFAULT_ITEM, parent=None):
        super().__init__(name, state, detail, detail_type, ObjectType.ITEM, parent)

        # 상태 속성
        self.hunger_recovery_value = 0
        self.fatigue_recovery_value = 0
        self.health_recovery_value = 0
        self.mana_recovery_value = 0

    def set_hunger_recovery_value(self, hunger_recovery_value):
        self.hunger_recovery_value = hunger_recovery_value

    def set_fatigue_recovery_value(self, fatigue_recovery_value):
        self.fatigue_recovery_value = fatigue_recovery_value

    def set_health_recovery_value(self, health_recovery_value):
        self.health_recovery_value = health_recovery_value

    def set_mana_recovery_value(self, mana_recovery_value):
        self.mana_recovery_value = mana_recovery_value