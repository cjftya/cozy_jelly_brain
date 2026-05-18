import random

class WeatherEngine:
    def __init__(self):
        self.weather_list = {
            "맑음": 60,
            "흐림": 20,
            "비": 10,
            "눈": 5,
            "천둥": 3,
            "번개": 2
        }
        self.weather = "맑음"
        self.remaining_hours = 3  # 현재 날씨가 유지될 남은 시간

    def tick(self, time_scale, season):
        """
        time_scale: 이번 틱에 경과한 가상 시간 (단위: 시간)
        season: 타임엔진에서 받아온 현재 계절 ("봄", "여름", "가을", "겨울")
        """
        self.remaining_hours -= time_scale

        # 유지 시간이 다 끝났거나, 여름에 눈이 내리는 어색한 상황이면 날씨 새로 갱신
        if self.remaining_hours <= 0 or (season == "여름" and self.weather == "눈"):
            self._update_weather(season)
            self.remaining_hours = random.randint(3, 12)

    def _update_weather(self, season):
        weathers = list(self.weather_list.keys())
        weights = list(self.weather_list.values())
        
        new_weather = random.choices(weathers, weights)[0]

        # 계절별 최소한의 자연스러운 예외 처리
        if season == "여름" and new_weather == "눈":
            new_weather = "비"
        elif season in ["봄", "가을"] and new_weather == "눈":
            new_weather = "흐림"

        self.weather = new_weather

    def force_weather(self, weather_name, duration=None):
        """
        외부에서 날씨를 강제로 설정합니다.
        
        :param weather_name: 강제 설정할 날씨 이름 ("맑음", "비", "눈" 등)
        :param duration: 강제 설정한 날씨가 유지될 시간 (단위: 시간)
                         None이면 기본 3~12시간 중 랜덤 설정됩니다.
                         무한히 고정하고 싶다면 float('inf')를 넣으면 됩니다.
        """
        if weather_name in self.weather_list:
            self.weather = weather_name
            if duration is not None:
                self.remaining_hours = duration
            else:
                self.remaining_hours = random.randint(3, 12)
        else:
            print(f"[경고] '{weather_name}'은(는) 등록되지 않은 날씨입니다.")

    def get_context(self):
        weather_description_dict = {
            "맑음": "하늘은 파랗고 구름 한 점 없이 맑습니다. 햇살이 따스하게 내리쬡니다.",
            "흐림": "하늘 전체가 두터운 회색 구름으로 덮여 있습니다. 빛이 약하게 들어옵니다.",
            "비": "톡톡 떨어지는 빗방울 소리가 들립니다. 공기 중에 물 향기가 감돕니다.",
            "눈": "하늘에서 하얀 눈송이가 소리 없이 내려앉고 있습니다. 주변이 고요합니다.",
            "천둥": "멀리서 낮게 '우르릉'거리는 소리가 들려옵니다. 곧 비가 올 것 같습니다.",
            "번개": "하늘이 번쩍이며 순간적으로 밝아졌다가 다시 어두워집니다. 곧 천둥이 칠 것입니다."
        }

        description = weather_description_dict.get(self.weather, self.weather)
        return f"""\
# 세계 날씨 정보 (World Weather Info)
- 현재 날씨: {self.weather}
- 날씨 설명: {description}"""