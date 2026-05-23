class TimeEngine:
    def __init__(self, start_year=3000, start_month=1, start_day=1, start_hour=8):
        """
        가상 세계의 초기 시작 시간을 설정합니다.
        기본값: 3000년 1월 1일 8시
        """
        self.days_in_month = 30
        self.seconds_to_advance = 60  # 턴당 60초
        self.time_scale = self.seconds_to_advance / 3600
        
        # 시작 날짜를 가상 세계의 '총 누적 초(Total Seconds)'로 환산
        total_days = (
            ((start_year - 1) * 12 * self.days_in_month) + 
            ((start_month - 1) * self.days_in_month) + 
            (start_day - 1)
        )
        self.total_virtual_seconds = (total_days * 24 * 3600) + (start_hour * 3600)

        # 상태 변수 초기화
        self.year = start_year
        self.month = start_month
        self.day = start_day
        self.hour = start_hour
        self.minute = 0
        self.second = 0
        
        self.day_of_week = ""
        self.season = ""
        self.day_cycle = ""

        # 초기 상태 계산
        self._update_all_states()

    def tick(self):
        """
        한 번의 틱(호출)마다 가상 세계의 시간을 원하는 초만큼 전진시킵니다.
        - seconds_to_advance=60 : 1틱당 1분 경과 (기본값)
        - seconds_to_advance=3600 : 1틱당 1시간 경과
        """
        self.total_virtual_seconds += self.seconds_to_advance
        self._update_all_states()

    def _update_all_states(self):
        """누적된 총 가상 초를 바탕으로 년/월/일/시/분/초 및 환경 요소를 변환합니다."""
        total_secs = int(self.total_virtual_seconds)

        # 1. 시/분/초 분해 (60초, 60분, 24시간 제한)
        self.second = total_secs % 60
        total_mins = total_secs // 60
        
        self.minute = total_mins % 60
        total_hours = total_mins // 60
        
        self.hour = total_hours % 24
        total_days = total_hours // 24

        # 2. 년/월/일 분해 (달력 기준 1부터 시작하도록 +1 처리)
        self.day = (total_days % self.days_in_month) + 1
        total_months = total_days // self.days_in_month
        
        self.month = (total_months % 12) + 1
        self.year = (total_months // 12) + 1

        # 3. 환경 파생 데이터 업데이트
        self._update_day_of_week(total_days)
        self._update_season()
        self._update_day_cycle()

    def _update_day_of_week(self, total_days):
        # 일주일 주기는 누적된 총 일수(total_days)를 기준으로 계산합니다.
        days_of_week = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
        self.day_of_week = days_of_week[total_days % 7]

    def _update_season(self):
        # 1~12월 범위 내에서 깔끔하게 매핑
        if self.month in [3, 4, 5]:
            self.season = "봄"
        elif self.month in [6, 7, 8]:
            self.season = "여름"
        elif self.month in [9, 10, 11]:
            self.season = "가을"
        else:
            self.season = "겨울"

    def _update_day_cycle(self):
        # 0~23시 범위를 기준으로 조금 더 몰입감 있게 세분화 가능합니다.
        if 6 <= self.hour < 11:
            self.day_cycle = "아침"
        elif 11 <= self.hour < 17:
            self.day_cycle = "낮"
        elif 17 <= self.hour < 21:
            self.day_cycle = "저녁"
        else:
            self.day_cycle = "밤"

    def get_date(self):
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d}"

    def get_clock(self):
        return f"{self.hour:02d}:{self.minute:02d}:{self.second:02d}"

    def get_context(self):
        # 텍스트가 정렬되도록 :02d 포맷(두 자리 숫자 맞춤)을 적용했습니다.
        return f"""\
# 세계 시간 정보 (World Time Info)
- 현재 시간: {self.year}년 {self.month:02d}월 {self.day:02d}일 {self.hour:02d}:{self.minute:02d}:{self.second:02d}
- 시간대: {self.day_cycle}
- 요일: {self.day_of_week}
- 계절: {self.season}"""