from config import *
import math

class Body:
    def __init__(self, x, y, mass, radius, color, vx=0, vy=0):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.mass = mass
        self.radius = radius
        self.color = color
        self.points = []

    def translate_coords(self, wx, wy, planet_ref):
        sx = ((wx - planet_ref.x) / MPP) + (W/2)
        sy = (H/2) - ((wy - planet_ref.y) / MPP)
        return (sx, sy)
    
    def translatePoint(self, planet_reference):
        return self.translate_coords(self.x, self.y, planet_reference)
    
    def translateRadius(self):
        return self.radius / MPP
    
    def update_trail(self):
        self.points.append((self.x, self.y))
        if len(self.points) > 1500:
            self.points.pop(0)