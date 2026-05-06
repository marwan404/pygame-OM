import pygame
import pygame.gfxdraw


class RenderContext:
    def __init__(self, surface, Star, W, H, scale):
        self.surface = surface
        self.Star = Star
        self.W = W
        self.H = H
        self.scale = scale


def draw_trail(b, mpp, ctx):
    if len(b.points) > 1:
        screen_pts = [
            b.translate_coords(p[0], p[1], mpp, ctx.W, ctx.H, ctx.Star)
            for p in b.points
        ]

        # scale points
        screen_pts = [(x * ctx.scale, y * ctx.scale) for (x, y) in screen_pts]

        pygame.draw.aalines(
            ctx.surface, b.color if b != ctx.Star else "white", False, screen_pts
        )


def draw_debug(sim, bodies, mpp, ctx):
    bx_w, by_w = sim.get_barycenter(bodies)
    bx_s, by_s = ctx.Star.translate_coords(bx_w, by_w, mpp, ctx.W, ctx.H, ctx.Star)

    bx_s *= ctx.scale
    by_s *= ctx.scale

    pygame.gfxdraw.filled_circle(
        ctx.surface, int(bx_s), int(by_s), 4 * ctx.scale, (255, 255, 0)
    )
    pygame.gfxdraw.aacircle(
        ctx.surface, int(bx_s), int(by_s), 4 * ctx.scale, (255, 255, 0)
    )

    for i, body_a in enumerate(bodies):
        pos_a = body_a.translatePoint(mpp, ctx.W, ctx.H, ctx.Star)
        pos_a = (pos_a[0] * ctx.scale, pos_a[1] * ctx.scale)

        # Line to barycenter
        pygame.draw.aaline(ctx.surface, (150, 150, 100), (bx_s, by_s), pos_a)

        for body_b in bodies[i + 1 :]:
            pos_b = body_b.translatePoint(mpp, ctx.W, ctx.H, ctx.Star)
            pos_b = (pos_b[0] * ctx.scale, pos_b[1] * ctx.scale)

            pygame.draw.aaline(ctx.surface, (100, 100, 80), pos_a, pos_b)


def draw_frame(bodies, mpp, ctx):
    for b in bodies:
        sx, sy = b.translatePoint(mpp, ctx.W, ctx.H, ctx.Star)

        # scale position
        sx *= ctx.scale
        sy *= ctx.scale

        if (
            -100 * ctx.scale <= sx <= ctx.W * ctx.scale + 100 * ctx.scale
            and -100 * ctx.scale <= sy <= ctx.H * ctx.scale + 100 * ctx.scale
        ):
            drawn_radius = max(1, int(b.translateRadius(mpp) * ctx.scale))

            pygame.gfxdraw.filled_circle(
                ctx.surface, int(sx), int(sy), drawn_radius, b.color
            )
            pygame.gfxdraw.aacircle(
                ctx.surface, int(sx), int(sy), drawn_radius, b.color
            )

        b.update_trail()
        draw_trail(b, mpp, ctx)
