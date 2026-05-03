# contains the physics

class Integrator:
    def __init__(self, G):
        self.G = G

    def get_acceleration(self, body, others):
        total_ax, total_ay = 0, 0
        epsilon = 0.1

        for other in others:
            if other is body:
                continue

            dx = other.x - body.x
            dy = other.y - body.y

            r_sq = dx*dx + dy*dy + epsilon**2
            r = r_sq**0.5

            # collision check
            if r <= body.radius + other.radius:
                # idk what to do here so ill leave it empty ig
                continue

            a = self.G * (other.mass / r_sq)

            total_ax += a * (dx / r)
            total_ay += a * (dy / r)

        return total_ax, total_ay
    
class EulerIntegrator(Integrator):
    def step(self, bodies, dt):
        # 1. Get all accelerations first (Simultaneous update)
        a = [self.get_acceleration(b, bodies) for b in bodies]
        
        # 2. Apply to bodies
        for i, b in enumerate(bodies):
            ax, ay = a[i]
            b.vx += ax * dt
            b.vy += ay * dt
            b.x += b.vx * dt
            b.y += b.vy * dt

class VerletIntegrator(Integrator):
    def step(self, bodies, dt):
        # 1. Get initial accelerations
        a_t = [self.get_acceleration(b, bodies) for b in bodies]
        
        # 2. Half-step position update for all
        for i, b in enumerate(bodies):
            ax_t, ay_t = a_t[i]
            b.x += (b.vx * dt) + (0.5 * ax_t * (dt**2))
            b.y += (b.vy * dt) + (0.5 * ay_t * (dt**2))
            
        # 3. Get new accelerations at the new positions
        a_next = [self.get_acceleration(b, bodies) for b in bodies]
        
        # 4. Correct velocities for all
        for i, b in enumerate(bodies):
            ax_t, ay_t = a_t[i]
            ax_n, ay_n = a_next[i]
            b.vx += 0.5 * (ax_t + ax_n) * dt
            b.vy += 0.5 * (ay_t + ay_n) * dt