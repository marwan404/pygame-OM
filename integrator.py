class Integrator:
    def __init__(self, G):
        self.G = G

    def get_differences(body, other):
        dx = other.x - body.x
        dy = other.y - body.y

        return dx, dy

    def get_distances(self, body, others):
        distances = []
        for other in others:
            if other is body: 
                distances.append(0)  
                continue
            
            dx, dy = self.get_differences(body, other)

            r_sq = pow(dx, 2) + pow(dy, 2)
            distances.append(r_sq)
        
        return distances

    def get_acceleration(self, body, others):
        total_ax, total_ay = 0, 0
        distances = self.get_distances(body, others)
        for i, other in enumerate(others):
            if other is body:
                continue

            dx, dy = self.get_differences(body, other)

            r = max(pow(distances[i], 0.5), 0.1) # Softening to prevent div by zero

            # a = G * M / r^2
            a = self.G * (other.mass / distances[i])
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