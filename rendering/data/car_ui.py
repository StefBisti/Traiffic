import math


class CarUI:
    # x, y - position of the car
    # vx, vy - speed of the car, used for facing direction
    def __init__(self, id, x, y, vx, vy, is_rl = False):
        self.id = id
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

    # math
    def get_direction(self):
        return math.degrees(math.atan2(-self.vy, self.vx)) - 90
