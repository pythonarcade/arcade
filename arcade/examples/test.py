"""This is an example on how the autogeometry can be used for deformable
terrain.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.test
"""
__docformat__ = "reStructuredText"

import sys

import pygame
from pygame.locals import *
from pygame.color import *

import pymunk
from pymunk import Vec2d, BB
import pymunk.pygame_util
import pymunk.autogeometry


def draw_helptext(screen):
    font = pygame.font.Font(None, 16)
    text = ["LMB(hold): Draw pink color",
            "LMB(hold) + Shift: Create balls",
            "g: Generate segments from pink color drawing",
            "r: Reset",
            ]
    y = 5
    for line in text:
        text = font.render(line, 1, THECOLORS["black"])
        screen.blit(text, (5, y))
        y += 10


def generate_geometry(surface, space):
    for s in space.shapes:
        if hasattr(s, "generated") and s.generated:
            space.remove(s)

    def sample_func(point):
        try:
            p = int(point.x), int(point.y)
            color = surface.get_at(p)
            return color.hsla[2]  # use lightness
        except:
            return 0

    line_set = pymunk.autogeometry.PolylineSet()

    def segment_func(v0, v1):
        line_set.collect_segment(v0, v1)

    pymunk.autogeometry.march_soft(
        BB(0, 0, 599, 599), 60, 60, 90, segment_func, sample_func)

    for polyline in line_set:
        line = pymunk.autogeometry.simplify_curves(polyline, 1.)

        for i in range(len(line) - 1):
            p1 = line[i]
            p2 = line[i + 1]
            shape = pymunk.Segment(space.static_body, p1, p2, 1)
            shape.friction = .5
            shape.color = pygame.color.THECOLORS["red"]
            shape.generated = True
            space.add(shape)


def main():
    pygame.init()
    screen = pygame.display.set_mode((600, 600))
    clock = pygame.time.Clock()

    space = pymunk.Space()
    space.gravity = 0, 980
    static = [
        pymunk.Segment(space.static_body, (0, -50), (-50, 650), 5),
        pymunk.Segment(space.static_body, (0, 650), (650, 650), 5),
        pymunk.Segment(space.static_body, (650, 650), (650, -50), 5),
        pymunk.Segment(space.static_body, (-50, -50), (650, -50), 5),
    ]
    for s in static:
        s.collision_type = 1
    space.add(static)

    def pre_solve(arb, space, data):
        s = arb.shapes[0]
        space.remove(s.body, s)
        return False

    space.add_collision_handler(0, 1).pre_solve = pre_solve

    terrain_surface = pygame.Surface((600, 600))
    terrain_surface.fill(pygame.color.THECOLORS["white"])

    color = pygame.color.THECOLORS["pink"]
    pygame.draw.circle(terrain_surface, color, (450, 120), 100)
    generate_geometry(terrain_surface, space)
    for x in range(25):
        mass = 1
        moment = pymunk.moment_for_circle(mass, 0, 10)
        body = pymunk.Body(mass, moment)
        body.position = 450, 120
        shape = pymunk.Circle(body, 10)
        shape.friction = .5
        space.add(body, shape)

    draw_options = pymunk.pygame_util.DrawOptions(screen)
    pymunk.pygame_util.positive_y_is_up = False

    fps = 60
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or \
                    event.type == KEYDOWN and (event.key in [K_ESCAPE, K_q]):
                sys.exit(0)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                pass
            elif event.type == KEYDOWN and event.key == K_r:
                terrain_surface.fill(pygame.color.THECOLORS["white"])
                for s in space.shapes:
                    if hasattr(s, "generated") and s.generated:
                        space.remove(s)

            elif event.type == KEYDOWN and event.key == K_g:
                generate_geometry(terrain_surface, space)

            elif event.type == KEYDOWN and event.key == K_p:
                pygame.image.save(screen, "deformable.png")

        if pygame.mouse.get_pressed()[0]:
            if pygame.key.get_mods() & KMOD_SHIFT:
                mass = 1
                moment = pymunk.moment_for_circle(mass, 0, 10)
                body = pymunk.Body(mass, moment)
                body.position = event.pos
                shape = pymunk.Circle(body, 10)
                shape.friction = .5
                space.add(body, shape)
            else:
                color = pygame.color.THECOLORS["pink"]
                pos = pygame.mouse.get_pos()
                pygame.draw.circle(terrain_surface, color, pos, 25)

        space.step(1. / fps)

        screen.fill(pygame.color.THECOLORS["white"])
        screen.blit(terrain_surface, (0, 0))
        space.debug_draw(draw_options)
        draw_helptext(screen)
        pygame.display.flip()

        clock.tick(fps)
        pygame.display.set_caption("fps: " + str(clock.get_fps()))


if __name__ == '__main__':
    sys.exit(main())
