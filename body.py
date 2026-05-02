from config import *
import math

class Body:
    def __init__(self, x, y, mass, radius, color, vx=0, vy=0):
        self.x = x
        self.y = y
        self.mass = mass
        self.radius = radius
        self.color = color
        self.vx = vx
        self.vy = vy
        self.points = []

    def translate_coords(self, wx, wy, planet_ref):
        sx = ((wx - planet_ref.x) / MPP) + (W/2)
        sy = (H/2) - ((wy - planet_ref.y) / MPP)
        return (sx, sy)
    
    def translatePoint(self, planet_reference):
        return self.translate_coords(self.x, self.y, planet_reference)
    
    def translateRadius(self):
        return self.radius / MPP
    
    def get_acceleration(self, others, G):
        total_ax, total_ay = 0, 0
        for other in others:
            if other is self:
                continue
            
            # find distance
            dx = other.x - self.x
            dy = other.y - self.y
            
            r_sq = pow(dx, 2) + pow(dy, 2)
            r = max(math.sqrt(r_sq),0.1)

            # collision check
            if r <= self.radius + other.radius:
                self.vx, self.vy = 0, 0
                continue
            
            # find acceleration f = ma, f = G(Mm/r2), f = f, ma = G(Mm/r2), a = G(M/r2)
            a = G * (other.mass / r_sq)
            total_ax += a * (dx / r)
            total_ay += a * (dy / r)
        
        return total_ax, total_ay
    
    def simulate_euler(self, others, dt, G):
        ax, ay = self.get_acceleration(others, G)

        # update velocities
        self.vx += ax * dt
        self.vy += ay * dt

        # update position
        self.x += self.vx * dt
        self.y += self.vy * dt
    
    def simulate_verlet(self, others, dt, G):
        # first acceleration
        ax_t, ay_t = self.get_acceleration(others, G)

        # half step logic
        self.x += (self.vx * dt) + (0.5 * ax_t * pow(dt, 2))
        self.y += (self.vy * dt) + (0.5 * ay_t * pow(dt, 2))

        # second acceleration
        ax_n, ay_n = self.get_acceleration(others, G)

        # velocity correction
        self.vx += 0.5 * (ax_t + ax_n) * dt
        self.vy += 0.5 * (ay_t + ay_n) * dt

    def update_trail(self):
        self.points.append((self.x, self.y))
        if len(self.points) > 1500:
            self.points.pop(0)