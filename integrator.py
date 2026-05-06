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

            r_sq = dx * dx + dy * dy + epsilon**2
            r = r_sq**0.5

            a = self.G * (other.mass / r_sq)

            total_ax += a * (dx / r)
            total_ay += a * (dy / r)

        return total_ax, total_ay

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
                    # 1. Choose the bigger one
                    winner, loser = (
                        (body_a, body_b)
                        if body_a.mass >= body_b.mass
                        else (body_b, body_a)
                    )

                    # 2. Conserve Momentum: v_new = (m1v1 + m2v2) / (m1 + m2)
                    total_mass = winner.mass + loser.mass
                    winner.vx = (
                        winner.mass * winner.vx + loser.mass * loser.vx
                    ) / total_mass
                    winner.vy = (
                        winner.mass * winner.vy + loser.mass * loser.vy
                    ) / total_mass

                    # 3. Absorb mass
                    winner.mass = total_mass
                    winner.radius = (winner.radius**2 + loser.radius**2) ** 0.5

                    to_remove.add(loser)

        # Return only the survivors
        return [b for b in bodies if b not in to_remove]

    @staticmethod
    def get_barycenter(bodies):
        total_mass = 0
        sum_mx = 0
        sum_my = 0

        for body in bodies:
            total_mass += body.mass
            sum_mx += body.mass * body.x
            sum_my += body.mass * body.y

        if total_mass == 0:
            return (0, 0)

        return (sum_mx / total_mass, sum_my / total_mass)


class EulerIntegrator(Integrator):
    def step(self, bodies, dt):
        # 1. Get all accelerations first
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
