import pygame


class IOContext:
    def __init__(self, dt, mpp, debug, fullscreen, screen, scale):
        self.dt = dt
        self.mpp = mpp
        self.debug = debug
        self.fullscreen = fullscreen
        self.screen = screen
        self.scale = scale


def slow_time(ctx):
    ctx.dt *= 0.5


def fast_time(ctx):
    ctx.dt *= 2.0


def zoom_in(ctx):
    ctx.mpp *= 0.8


def zoom_out(ctx):
    ctx.mpp *= 1.2


def toggle_debug(ctx):
    ctx.debug = 1 - ctx.debug


def toggle_fullscreen(ctx):
    ctx.fullscreen = not ctx.fullscreen

    if ctx.fullscreen:
        ctx.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        ctx.screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)

    W, H = ctx.screen.get_size()

    ctx.W = W
    ctx.H = H

    ctx.surface = pygame.Surface((W * ctx.scale, H * ctx.scale))


key_actions = {
    pygame.K_COMMA: slow_time,
    pygame.K_PERIOD: fast_time,
    pygame.K_i: zoom_in,
    pygame.K_o: zoom_out,
    pygame.K_1: toggle_debug,
    pygame.K_f: toggle_fullscreen,
}
