import pygame
from integrator import EulerIntegrator, VerletIntegrator
from random_system_generator import generate_random_system
from config import *
from actions import *
from drawing_helpers import *


# pygame setup
pygame.init()
clock = pygame.time.Clock()
running = True


# setup
dt = 1 / 6
mpp = 100

fullscreen = True
W = pygame.display.Info().current_w
H = pygame.display.Info().current_h

scale = 2
render_surface = pygame.Surface((W * scale, H * scale))

bodies = generate_random_system()
Star = max(bodies, key=lambda b: b.mass)
ctx = RenderContext(render_surface, Star, W, H, scale)

debug = 0


# identify sim
mode = int(input("type 1 for euler and type 2 for verlet: "))
if mode == 1:
    sim = EulerIntegrator(G)
else:
    sim = VerletIntegrator(G)


screen = pygame.display.set_mode(
    (W, H), pygame.RESIZABLE | pygame.FULLSCREEN | pygame.HWACCEL | pygame.HWSURFACE
)
icon = pygame.image.load("screenshots/binary-system-orbitting-barycenter.png")
pygame.display.set_icon(icon)
pygame.display.set_caption("orbital simulation")

ioctx = IOContext(dt, mpp, debug, fullscreen, screen, scale)


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.VIDEORESIZE:
            W, H = pygame.display.get_surface().get_size()
            render_surface = pygame.Surface((W * scale, H * scale))
            ctx.surface = render_surface
            ioctx.W = W
            ioctx.H = H
            ctx.W = W
            ctx.H = H

        if event.type == pygame.KEYDOWN:
            action = key_actions.get(event.key)
            if action:
                action(ioctx)

    # Physics Sub-stepping
    sub = 10
    for _ in range(sub):
        sim.step(bodies, ioctx.dt / sub)

    render_surface.fill("black")

    # Update survivors
    bodies = sim.resolve_collisions(bodies)

    # Draw Debug Web
    if ioctx.debug == 1 and len(bodies) > 0:
        draw_debug(sim, bodies, ioctx.mpp, ctx)

    # Draw full frame
    draw_frame(bodies, ioctx.mpp, ctx)

    smooth = pygame.transform.smoothscale(render_surface, (W, H))
    screen.blit(smooth, (0, 0))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
