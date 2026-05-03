class Integrator:
    def __init__(self, G):
        self.G = G

    def get_acceleration(self, body, others):
        total_ax, total_ay = 0, 0
        for other in others:
            if other is body:
                continue
            
            dx = other.x - body.x
            dy = other.y - body.y
            r_sq = (dx**2) + (dy**2)
            r = max(r_sq**0.5, 0.1) # Softening to prevent div by zero

            # a = G * M / r^2
            a = self.G * (other.mass / r_sq)
            total_ax += a * (dx / r)
            total_ay += a * (dy / r)
            
        return total_ax, total_ay
    
class EulerIntegrator(Integrator):
    def step(self, bodies, dt):
        # 1. Get all accelerations first (Simultaneous update)
        accels = [self.get_acceleration(b, bodies) for b in bodies]
        
        # 2. Apply to bodies
        for i, b in enumerate(bodies):
            ax, ay = accels[i]
            b.vx += ax * dt
            b.vy += ay * dt
            b.x += b.vx * dt
            b.y += b.vy * dt

class VerletIntegrator(Integrator):
    def step(self, bodies, dt):
        # 1. Get initial accelerations
        accels_t = [self.get_acceleration(b, bodies) for b in bodies]
        
        # 2. Half-step position update for all
        for i, b in enumerate(bodies):
            ax_t, ay_t = accels_t[i]
            b.x += (b.vx * dt) + (0.5 * ax_t * (dt**2))
            b.y += (b.vy * dt) + (0.5 * ay_t * (dt**2))
            
        # 3. Get new accelerations at the new positions
        accels_next = [self.get_acceleration(b, bodies) for b in bodies]
        
        # 4. Correct velocities for all
        for i, b in enumerate(bodies):
            ax_t, ay_t = accels_t[i]
            ax_n, ay_n = accels_next[i]
            b.vx += 0.5 * (ax_t + ax_n) * dt
            b.vy += 0.5 * (ay_t + ay_n) * dt