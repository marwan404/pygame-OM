# contains the main game loop

import pygame
import pygame.gfxdraw
import random
import math
from body import Body
from integrator import EulerIntegrator, VerletIntegrator
from config import *

# pygame setup
pygame.init()
clock = pygame.time.Clock()
running = True

# setup

dt = 1/2
mpp = 100

W = pygame.display.Info().current_w
H = pygame.display.Info().current_h

scale = 2
render_surface = pygame.Surface((W * scale, H * scale))

STAR_COLORS = [
    (255, 94, 0), 
    (255, 140, 20), 
    (255, 180, 60), 
    (255, 220, 120)
]

PLANET_COLORS = [
    (34, 98, 176),
    (198, 134, 66),
    (92, 184, 120),
    (156, 156, 156),
    (121, 82, 179),
    (210, 90, 70),
    (60, 170, 200),
    (180, 200, 120),
    (145, 110, 85),
    (75, 75, 110)
]


# FUNCTIONS

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

def draw_trail(b, Star_ref):
    if len(b.points) > 1:
        screen_pts = [
            b.translate_coords(p[0], p[1], mpp, W, H, Star_ref)
            for p in b.points
        ]

        # scale points
        screen_pts = [(x * scale, y * scale) for (x, y) in screen_pts]

        pygame.draw.aalines(
            render_surface,
            b.color if b != Star else "white",
            False,
            screen_pts
        )

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

def draw_debug():
    bx_w, by_w = get_barycenter(bodies)
    bx_s, by_s = Star.translate_coords(bx_w, by_w, mpp, W, H, Star)

    bx_s *= scale
    by_s *= scale

    pygame.gfxdraw.filled_circle(render_surface, int(bx_s), int(by_s), 4 * scale, (255, 255, 0))
    pygame.gfxdraw.aacircle(render_surface, int(bx_s), int(by_s), 4 * scale, (255, 255, 0))

    for i, body_a in enumerate(bodies):
        pos_a = body_a.translatePoint(mpp, W, H, Star)
        pos_a = (pos_a[0] * scale, pos_a[1] * scale)

        # Line to barycenter
        pygame.draw.aaline(render_surface, (150, 150, 100), (bx_s, by_s), pos_a)

        for body_b in bodies[i+1:]:
            pos_b = body_b.translatePoint(mpp, W, H, Star)
            pos_b = (pos_b[0] * scale, pos_b[1] * scale)

            pygame.draw.aaline(render_surface, (100, 100, 80), pos_a, pos_b)

# b4 gameloop prep
mode = int(input("type 1 for euler and type 2 for verlet: "))
debug = int(input("enter 1 for debug mode lines and enter 0 for normal mode: "))

bodies = generate_random_system()
Star = max(bodies, key=lambda b: b.mass) #star is whatever is the heaviest

if mode == 1:
    sim = EulerIntegrator(G)
else:
    sim = VerletIntegrator(G)

fullscreen = True
screen = pygame.display.set_mode((W,H), pygame.RESIZABLE | pygame.FULLSCREEN | pygame.HWACCEL | pygame.HWSURFACE)
icon = pygame.image.load("screenshots/binary-system-orbitting-barycenter.png")
pygame.display.set_icon(icon)
pygame.display.set_caption("orbital simulation")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.VIDEORESIZE:
            W, H = pygame.display.get_surface().get_size()
            render_surface = pygame.Surface((W * scale, H * scale))
        if event.type == pygame.KEYDOWN:
            # Time warp
            if event.key == pygame.K_COMMA:
                dt *= 0.5
            elif event.key == pygame.K_PERIOD:
                dt *= 2.0
            # Zoom
            elif event.key == pygame.K_i:
                mpp *= 0.8 # Zoom in
            elif event.key == pygame.K_o:
                mpp *= 1.2 # Zoom out
            # debug mode
            elif event.key == pygame.K_1:
                if debug == 1:
                    debug = 0
                else:
                    debug = 1
            # Press 'F' to toggle fullscreen
            elif event.key == pygame.K_f: 
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)

    # 1. Physics Sub-stepping
    sub = 10 
    for _ in range(sub):
        sim.step(bodies, dt / sub)

    render_surface.fill("black")

    # 2. Update survivors
    bodies = sim.resolve_collisions(bodies)

    # 3. Draw Debug Web
    if debug == 1 and len(bodies) > 0:
        draw_debug()

    # 4. Draw Bodies and Trails
    for b in bodies:
        sx, sy = b.translatePoint(mpp, W, H, Star)

        # scale position
        sx *= scale
        sy *= scale

        if -100*scale <= sx <= W*scale + 100*scale and -100*scale <= sy <= H*scale + 100*scale:
            
            drawn_radius = max(1, int(b.translateRadius(mpp) * scale))

            pygame.gfxdraw.filled_circle(render_surface, int(sx), int(sy), drawn_radius, b.color)
            pygame.gfxdraw.aacircle(render_surface, int(sx), int(sy), drawn_radius, b.color)

        # Update trails regardless of screen position so they don't break when off-screen
        b.update_trail()
        draw_trail(b, Star)

    smooth = pygame.transform.smoothscale(render_surface, (W, H))
    screen.blit(smooth, (0, 0))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()