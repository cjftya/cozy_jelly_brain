from log import Logger

class PersonalityMatrix:

    def __init__(self):
        # 성격 매트릭스 (0 ~ 1.0)
        # logic_emotion : 감성적인가 이성적인가
        # defensive_open : 방어적인가 개방적인가
        # fear_decisive : 공포에 우유부단한가 용감하고 단호한가
        # obedient_rebellious : 복종적인가 반항적인가
        # curiosity_indifference : 호기심이 많은가 무관심한가
        self.matrix = {
            'logic_emotion': 0.50,
            'defensive_open': 0.50,
            'fear_decisive': 0.50,
            'obedient_rebellious': 0.50,
            'curiosity_indifference': 0.50
        }

    def update_personality_matrix(self, new_matrix):
        for key, value in new_matrix.items():
            if key not in self.matrix:
                continue
            self.matrix[key] = float(max(0.0, min(1.0, float(value))))

        Logger.log("Personality Matrix Updated", self.matrix)

    def get_matrix(self):
        return self.matrix

    def get_value(self, key, default=0.0):
        return self.matrix.get(key, default)

    def reset_value(self):
        self.matrix = {
            'logic_emotion': 0.50,
            'defensive_open': 0.50,
            'fear_decisive': 0.50,
            'obedient_rebellious': 0.50,
            'curiosity_indifference': 0.50
        }

    def set_value(self, logic_emotion=None, defensive_open=None, fear_decisive=None, 
                        obedient_rebellious=None, curiosity_indifference=None):
        if logic_emotion is not None:
            self.matrix['logic_emotion'] = logic_emotion
        if defensive_open is not None:
            self.matrix['defensive_open'] = defensive_open
        if fear_decisive is not None:
            self.matrix['fear_decisive'] = fear_decisive
        if obedient_rebellious is not None:
            self.matrix['obedient_rebellious'] = obedient_rebellious
        if curiosity_indifference is not None:
            self.matrix['curiosity_indifference'] = curiosity_indifference
