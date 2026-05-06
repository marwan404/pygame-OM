from config import *
import random
from body import Body
import math


def generate_random_system():
    bodies = []
    used_colors = []
    used_r = []

    # number of bodies (1 star + planets)
    n = random.randint(2, 10)

    # STAR
    star_mass = random.randint(15000, 50000)
    star_radius = star_mass / 10
    star_color = random.choice(STAR_COLORS)

    star = Body(0, star_mass, star_radius, star_color)
    bodies.append(star)

    # PLANETS
    for _ in range(n - 1):
        mass = random.uniform(star_mass * 0.0001, star_mass * 0.01)
        radius = mass

        # generate well-spaced orbit radius
        too_close = True
        while too_close:
            r = random.uniform(star.radius * 3, star.radius * 20)
            too_close = any(abs(r - prev) < star.radius * 2 for prev in used_r)

        used_r.append(r)

        # circular velocity
        vy = math.sqrt(G * star.mass / r)

        # safe color selection
        if len(used_colors) >= len(PLANET_COLORS):
            color = random.choice(PLANET_COLORS)
        else:
            color = random.choice(PLANET_COLORS)
            while color in used_colors:
                color = random.choice(PLANET_COLORS)
            used_colors.append(color)

        bodies.append(Body(r, mass, radius, color, vy=vy))

    # sort planets by distance (prevents crossing at spawn)
    bodies[1:] = sorted(bodies[1:], key=lambda b: b.x)

    # momentum balancing
    total_m_vy = sum(b.mass * b.vy for b in bodies[1:])
    star.vy = -total_m_vy / star.mass

    return bodies
