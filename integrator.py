import numpy as np
from numba import njit


@njit
def get_accelerations(x, y, mass, G):
    n = len(x)
    ax = np.zeros(n)
    ay = np.zeros(n)
    epsilon_sq = 0.1**2

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            
            dx = x[j] - x[i]
            dy = y[j] - y[i]
            r_sq = dx*dx + dy*dy + epsilon_sq
            r = r_sq**0.5
            
            f = G * mass[j] / r_sq
            ax[i] += f * (dx / r)
            ay[i] += f * (dy / r)
            
    return ax, ay


class Integrator:
    def __init__(self, G):
        self.G = G

    def resolve_collisions(self, bodies):
        to_remove = set()

        for i, body_a in enumerate(bodies):
            if body_a in to_remove:
                continue

            for body_b in bodies[i + 1 :]:
                if body_b in to_remove:
                    continue

                dx = body_b.x - body_a.x
                dy = body_b.y - body_a.y
                dist_sq = dx * dx + dy * dy
                min_dist = body_a.radius + body_b.radius

                if dist_sq <= min_dist**2:
                    winner, loser = (
                        (body_a, body_b)
                        if body_a.mass >= body_b.mass
                        else (body_b, body_a)
                    )

                    total_mass = winner.mass + loser.mass
                    winner.vx = (winner.mass * winner.vx + loser.mass * loser.vx) / total_mass
                    winner.vy = (winner.mass * winner.vy + loser.mass * loser.vy) / total_mass

                    winner.mass = total_mass
                    winner.radius = (winner.radius**2 + loser.radius**2) ** 0.5

                    to_remove.add(loser)

        return [b for b in bodies if b not in to_remove]


    @staticmethod
    def get_barycenter(bodies):
        total_mass = sum(b.mass for b in bodies)
        if total_mass == 0: return (0, 0)
        
        sum_mx = sum(b.mass * b.x for b in bodies)
        sum_my = sum(b.mass * b.y for b in bodies)
        
        return (sum_mx / total_mass, sum_my / total_mass)


class EulerIntegrator(Integrator):
    def step(self, bodies, dt):
        n = len(bodies)
        if n == 0: return
        
        # 1. Extract data to NumPy arrays
        x = np.array([b.x for b in bodies])
        y = np.array([b.y for b in bodies])
        mass = np.array([b.mass for b in bodies])

        # 2. get accelerations
        ax, ay = get_accelerations(x, y, mass, self.G)

        # 3. Apply back to objects
        for i, b in enumerate(bodies):
            b.vx += ax[i] * dt
            b.vy += ay[i] * dt
            b.x += b.vx * dt
            b.y += b.vy * dt


class VerletIntegrator(Integrator):
    def step(self, bodies, dt):
        n = len(bodies)
        if n == 0: return

        # extract data to numpy arrays
        x = np.array([b.x for b in bodies], dtype=np.float64)
        y = np.array([b.y for b in bodies], dtype=np.float64)
        vx = np.array([b.vx for b in bodies], dtype=np.float64)
        vy = np.array([b.vy for b in bodies], dtype=np.float64)
        mass = np.array([b.mass for b in bodies], dtype=np.float64)

        # initial accelerations
        ax_t, ay_t = get_accelerations(x, y, mass, self.G)

        # half step position update
        x += (vx * dt) + (0.5 * ax_t * (dt**2))
        y += (vy * dt) + (0.5 * ay_t * (dt**2))

        # new accelerations at new positions
        ax_n, ay_n = get_accelerations(x, y, mass, self.G)

        # correct velocities
        vx += 0.5 * (ax_t + ax_n) * dt
        vy += 0.5 * (ay_t + ay_n) * dt

        # update the object
        for i, b in enumerate(bodies):
            b.x = x[i]
            b.y = y[i]
            b.vx = vx[i]
            b.vy = vy[i]