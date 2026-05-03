# contains the body class

from config import *
from collections import deque

class Body:
    def __init__(self, x, mass, radius, color, y=0, vx=0, vy=0):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.mass = mass
        self.radius = radius
        self.color = color
        self.points = deque(maxlen=750)

    def translate_coords(self, wx, wy, mpp, star_ref):
        sx = ((wx - star_ref.x) / mpp) + (W/2)
        sy = (H/2) - ((wy - star_ref.y) / mpp)
        return (sx, sy)
    
    def translatePoint(self, mpp, star_ref):
        return self.translate_coords(self.x, self.y, mpp, star_ref)
    
    def translateRadius(self, mpp):
        return self.radius / mpp
    
    def update_trail(self):
        self.points.append((self.x, self.y))