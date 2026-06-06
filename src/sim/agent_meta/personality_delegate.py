from log import Logger

class PersonalityDelegate:

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

    def __getitem__(self, key):
        return self.matrix[key]

    def apply_state_delta(self, state_delta, base_step=0.05, critical_step=0.20):
        """ 
        LLM이 뱉은 5단계 방향(-2, -1, 0, 1, 2)에 따라 수치를 조절합니다.
        - 1 / -1 : 일상적인 자극 (0.05씩 서서히 변동)
        - 2 / -2 : 생존이나 자아에 직결된 극단적 충격 (0.20씩 급격히 변동)
        """
        for key, direction in state_delta.items():
            if key not in self.matrix:
                continue
            
            try:
                dir_val = int(direction)
                
                # 강한 증가/감소 (크리티컬)
                if dir_val == 2:
                    self.matrix[key] = min(1.0, self.matrix[key] + critical_step)
                elif dir_val == -2:
                    self.matrix[key] = max(0.0, self.matrix[key] - critical_step)
                
                # 일반 증가/감소
                elif dir_val == 1:
                    self.matrix[key] = min(1.0, self.matrix[key] + base_step)
                elif dir_val == -1:
                    self.matrix[key] = max(0.0, self.matrix[key] - base_step)
                    
            except ValueError:
                pass

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
