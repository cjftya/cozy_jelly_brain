from log import Logger

class RelationShipScoreMatrix:

    def __init__(self):
        self.matrix = {}

    def update_relationship_score_matrix(self, score_map):
        for name, score in score_map.items():
            if name not in self.matrix:
                continue
            self.matrix[name] = float(max(0.0, min(100.0, float(score))))
        
        Logger.log("Relationship Score Matrix Updated", self.matrix)

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