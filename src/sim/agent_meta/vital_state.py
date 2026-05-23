class GenderType:
    MALE = 0
    FEMALE = 1

class VitalState:
    def __init__(self):
        # 나이 및 수명 (소수점으로 미세하게 증가)
        self.age = 30.0
        self.life_span = 100.0

        # 성별
        self.gender = GenderType.FEMALE

        # 건강
        self.health = 100.0
        self.max_health = 100.0
        self.health_label = "최상"

        # 피로도
        self.fatigue = 0.0
        self.max_fatigue = 100.0

        # 식욕/허기
        self.hunger = 0.0
        self.max_hunger = 100.0
        
        # 사망 여부 플래그
        self.is_alive = True

        self.warning = ""

    def update_hunger(self, value):
        self.hunger = max(0.0, min(self.max_hunger, self.hunger + value))

    def update_fatigue(self, value):
        self.fatigue = max(0.0, min(self.max_fatigue, self.fatigue + value))

    def update_health(self, value):
        self.health = max(0.0, min(self.max_health, self.health + value))

    def tick(self, time_scale=1.0):
        if not self.is_alive:
            return

        # 1. 시간 경과에 따른 피로도 및 허기 증가
        # min()을 사용해 max_value를 넘지 않도록 제한
        self.fatigue = min(self.max_fatigue, self.fatigue + (1.0 * time_scale))
        self.hunger = min(self.max_hunger, self.hunger + (3.0 * time_scale))

        # 2. 상태 상호작용 (패널티 적용)
        # 배가 고프거나 너무 지치면 건강(health)이 깎임
        if self.hunger >= self.max_hunger:
            self.health = max(0.0, self.health - (2.0 * time_scale))
            
        if self.fatigue >= self.max_fatigue:
            self.health = max(0.0, self.health - (1.0 * time_scale))

        # 3. 자연 치유 메커니즘
        # 허기와 피로가 모두 낮은 상태(예: 30 미만)라면 건강 회복
        if self.hunger < 30.0 and self.fatigue < 30.0 and self.health < self.max_health:
            self.health = min(self.max_health, self.health + (0.5 * time_scale))

        # 건강 상태 직관적 라벨링
        if self.health > 80: self.health_label = "최상"
        elif self.health > 40: self.health_label = "보통"
        elif self.health > 15: self.health_label = "쇠약함"
        else: self.health_label = "위독함"

        # 4. 위급 경고 메시지 동적 생성
        alerts = []
        if self.hunger >= 80.0:
            alerts.append("배고픔이 심각합니다. 즉시 음식을 먹어야 합니다.")
        if self.fatigue >= 80.0:
            alerts.append("피로가 극에 달했습니다. 수면이나 휴식이 필요합니다.")
        if self.health <= 30.0:
            alerts.append("생명이 위태롭습니다. 무리한 활동을 피하고 회복에 집중하세요.")

        # 경고가 없으면 깔끔하게 비워두거나 정상 상태 표시
        self.warning = "\n".join(alerts) if len(alerts) > 0 else "특이사항 없음"

        # 4. 나이 증가 (시간 스케일 반영)
        # 예: 1 틱을 '1시간'이라고 가정할 때 -> 1년은 8760시간
        ticks_per_year = 360 * 24
        self.age += time_scale / ticks_per_year

        # 5. 사망 조건 검사
        if self.health <= 0.0 or self.age >= self.life_span:
            self.is_alive = False
            self.health = 0

    def get_context(self):
        gender_str = "FEMALE" if self.gender == GenderType.FEMALE else "MALE"

        return f"""\
- 나이: {self.age:.1f}세
- 성별: {gender_str}
- 건강도: {int(self.health)}/100 [{self.health_label}]
- 피로도: {int(self.fatigue)}/100
- 허기짐: {int(self.hunger)}/100
- 경고: {self.warning}"""