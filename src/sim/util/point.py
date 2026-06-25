class Point:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def set_value(self, x, y):
        self.x = x
        self.y = y

    def add_value(self, x, y):
        self.x += x
        self.y += y
