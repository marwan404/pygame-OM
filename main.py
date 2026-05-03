import pygame
from body import Body
from integrator import EulerIntegrator, VerletIntegrator
from config import *

# pygame setup
pygame.init()
screen = pygame.display.set_mode((W,H))
clock = pygame.time.Clock()
running = True

Planet_Mass = 50000
Planet_Radius = 500

r1 = 600 + Planet_Radius
r2 = 1000 + Planet_Radius

# Circular Velocities (v = sqrt(G*M/r))
v1 = (G * Planet_Mass / r1)**0.5
v2 = (G * Planet_Mass / r2)**0.5

Satellites = [
    Body(r1, 0, 150, 15, "red", 0, v1), 
    Body(r2, 0, 300, 30, "green", 0, v2)
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

mode = int(input("type 1 for euler and type 2 for verlet: "))

if mode == 1:
    sim = EulerIntegrator(G)
else:
    sim = VerletIntegrator(G)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Physics Sub-stepping
    SUB_STEPS = 10 
    for _ in range(SUB_STEPS):
        sim.step(bodies, DT / SUB_STEPS)

    screen.fill("black")
    
    # Update and Draw
    for b in bodies:
        pygame.draw.circle(screen, b.color, b.translatePoint(Planet), b.translateRadius())
        
        b.update_trail()
        draw_trail(b, Planet)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()