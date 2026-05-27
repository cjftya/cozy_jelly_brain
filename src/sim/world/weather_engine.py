import random
from sim.world.time_engine import SeasonType

class WeatherType:
    CLEAR = "맑음"
    CLOUDY = "흐림"
    RAINY = "비"
    SNOWY = "눈"
    THUNDERSTORM = "천둥"
    LIGHTNING = "번개"

class WeatherEngine:
    def __init__(self, weather_type=WeatherType.CLEAR, remaining_hours=3):
        self.weather_type_list = {
            WeatherType.CLEAR: 60,
            WeatherType.CLOUDY: 20,
            WeatherType.RAINY: 10,
            WeatherType.SNOWY: 5,
            WeatherType.THUNDERSTORM: 3,
            WeatherType.LIGHTNING: 2
        }
        self.weather_type = weather_type
        self.remaining_hours = remaining_hours  # 현재 날씨가 유지될 남은 시간

    def tick(self, time_scale, season):
        self.remaining_hours -= time_scale

        # 유지 시간이 다 끝났거나, 여름에 눈이 내리는 어색한 상황이면 날씨 새로 갱신
        if self.remaining_hours <= 0 or (season == SeasonType.SUMMER and self.weather_type == WeatherType.SNOWY):
            self._update_weather(season)
            self.remaining_hours = random.randint(3, 12)

    def _update_weather(self, season):
        weather_types = list(self.weather_type_list.keys())
        weights = list(self.weather_type_list.values())
        
        new_weather_type = random.choices(weather_types, weights)[0]

        # 계절별 최소한의 자연스러운 예외 처리
        if season == SeasonType.SUMMER and new_weather_type == WeatherType.SNOWY:
            new_weather_type = WeatherType.RAINY
        elif season in [SeasonType.SPRING, SeasonType.AUTUMN] and new_weather_type == WeatherType.SNOWY:
            new_weather_type = WeatherType.CLOUDY

        self.weather_type = new_weather_type

    def force_weather(self, weather_type, duration_hours=None):
        if weather_type in self.weather_type_list:
            self.weather_type = weather_type
            if duration_hours is not None:
                self.remaining_hours = duration_hours
            else:
                self.remaining_hours = random.randint(3, 12)
        else:
            print(f"[ERROR] '{weather_type}'은(는) 등록되지 않은 날씨입니다.")

    def get_weather_description(self, weather_type):
        weather_description_dict = {
            WeatherType.CLEAR: "하늘은 파랗고 구름 한 점 없이 맑습니다. 햇살이 따스하게 내리쬡니다.",
            WeatherType.CLOUDY: "하늘 전체가 두터운 회색 구름으로 덮여 있습니다. 빛이 약하게 들어옵니다.",
            WeatherType.RAINY: "톡톡 떨어지는 빗방울 소리가 들립니다. 공기 중에 물 향기가 감돕니다.",
            WeatherType.SNOWY: "하늘에서 하얀 눈송이가 소리 없이 내려앉고 있습니다. 주변이 고요합니다.",
            WeatherType.THUNDERSTORM: "멀리서 낮게 '우르릉'거리는 소리가 들려옵니다. 곧 비가 올 것 같습니다.",
            WeatherType.LIGHTNING: "하늘이 번쩍이며 순간적으로 밝아졌다가 다시 어두워집니다. 곧 천둥이 칠 것입니다."
        }
        return weather_description_dict.get(weather_type)

    def get_context(self):
        return f"""\
# 세계 날씨 정보 (World Weather Info)
- 현재 날씨: {self.weather_type}
- 날씨 설명: {self.get_weather_description(self.weather_type)}"""