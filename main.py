# contains the main game loop

import pygame
from body import Body
from integrator import EulerIntegrator, VerletIntegrator
from config import *

# pygame setup
pygame.init()
clock = pygame.time.Clock()
running = True

Planet_Mass = 50000
Planet_Radius = 5000

r1 = 2000 + Planet_Radius
r2 = 6000 + Planet_Radius
r3 = 9000 + Planet_Radius
r4 = 13000 + Planet_Radius

# Circular Velocities (v = sqrt(G*M/r))
v1 = (G * Planet_Mass / r1)**0.5
v2 = (G * Planet_Mass / r2)**0.5
v3 = (G * Planet_Mass / r3)**0.5
v4 = (G * Planet_Mass / r4)**0.5

Satellites = [
    Body(r1, 0, 150, 15, "red", 0, v1), 
    Body(r2, 0, 300, 30, "green", 0, v2),
    Body(r3, 0, 400, 40, "white", 0, v3),
    Body(r4, 0, 4000, 400, "pink", 0, v4)
]

# Balance momentum so the system doesn't drift
total_m_vy = sum(s.mass * s.vy for s in Satellites)
planet_vy = -total_m_vy / Planet_Mass

Planet = Body(0, 0, Planet_Mass, Planet_Radius, "blue", 0, planet_vy)
bodies = [Planet] + Satellites

def draw_trail(b, planet_ref):
    if len(b.points) > 1:
        screen_pts = [b.translate_coords(p[0], p[1], planet_ref) for p in b.points]
        pygame.draw.lines(screen, b.color if b != Planet else "white", False, screen_pts, 1)

def get_barycenter(bodies):
    total_mass = 0
    sum_mx = 0
    sum_my = 0

    for body in bodies:
        total_mass += body.mass
        sum_mx += body.mass * body.x
        sum_my += body.mass * body.y

    if total_mass == 0: return (0, 0)
    
    return (sum_mx / total_mass, sum_my / total_mass)

mode = int(input("type 1 for euler and type 2 for verlet: "))
debug = int(input("enter 1 for debug mode lines and enter 0 for normal mode: "))

if mode == 1:
    sim = EulerIntegrator(G)
else:
    sim = VerletIntegrator(G)

screen = pygame.display.set_mode((W,H))

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Physics Sub-stepping
    SUB_STEPS = 10 
    for _ in range(SUB_STEPS):
        sim.step(bodies, DT / SUB_STEPS)

    screen.fill("black")

    # Update survivors
    bodies = sim.resolve_collisions(bodies)

    if debug == 1:
        # calculate, translate and draw the barycenter
        bx_w, by_w = get_barycenter(bodies)
        bx_s, by_s = Planet.translate_coords(bx_w, by_w, Planet)
        pygame.draw.circle(screen, "yellow", (int(bx_s), int(by_s)), 4)
    
    # Draw
    for b in bodies:
        if not b.translatePoint(Planet) >= (W, H):
            if debug == 1:
                # draw line from body to barycenter
                pygame.draw.line(screen, (150,150,100), (bx_s, by_s), b.translatePoint(Planet), 1)

                # draw line connecting each body
                for other in bodies:
                    if other is b:
                        continue
                    else:
                        pygame.draw.line(screen, (150,150,100), other.translatePoint(Planet), b.translatePoint(Planet), 1)

            # draw body
            pygame.draw.circle(screen, b.color, b.translatePoint(Planet), b.translateRadius())

            # draw trail
            b.update_trail()
            draw_trail(b, Planet)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()