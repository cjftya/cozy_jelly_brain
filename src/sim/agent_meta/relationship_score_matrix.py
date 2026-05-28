from log import Logger

class RelationShipScoreMatrix:

    def __init__(self):
        self.matrix = {}

    def apply_relationship_delta(self, delta_map, base_step=5.0, critical_step=20.0):
        for name, direction in delta_map.items():
            # 처음 상호작용하는 대상이라면 기본 호감도 50으로 세팅
            if name not in self.matrix:
                self.matrix[name] = 50.0
            
            try:
                dir_val = int(direction)
                
                # 강한 호전/악화 (목숨을 구해주거나, 크게 배신했을 때)
                if dir_val == 2:
                    self.matrix[name] = min(100.0, self.matrix[name] + critical_step)
                elif dir_val == -2:
                    self.matrix[name] = max(0.0, self.matrix[name] - critical_step)
                
                # 일반적인 상호작용 (대화, 가벼운 도움 등)
                elif dir_val == 1:
                    self.matrix[name] = min(100.0, self.matrix[name] + base_step)
                elif dir_val == -1:
                    self.matrix[name] = max(0.0, self.matrix[name] - base_step)
                    
            except ValueError:
                pass

    def get_matrix(self):
        return self.matrix

    def get_value(self, name, default=0.0):
        return self.matrix.get(name, default)

    def reset_value(self):
        self.matrix = {}

    def set_value(self, name, score):
        self.matrix[name] = score

    def get_context(self, names):
        return ",".join([f"[{name}:{self.matrix.get(name, 0)}]" for name in names])