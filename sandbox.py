from typing import Tuple

import pygame as pg
from Math import GravityPool, draw_stick, draw_point, ObjectsPool

shape = GravityPool()

shape.generate_mesh()

pg.init()
display = pg.display.set_mode((600, 600))
done = False
fps = 60
clock = pg.time.Clock()
editing = True

creating_line = False
first_point = None


def round_tuple(tup: Tuple[int, int]):
    v1 = tup[0] + 12.5
    v2 = tup[1] + 12.5
    return v1 - v1 % 25, v2 - v2 % 25


while not done:
    if editing:
        for ev in pg.event.get():
            if ev.type == pg.QUIT:
                done = True
            elif ev.type == pg.MOUSEBUTTONDOWN:
                pos = round_tuple(ev.pos)
                if ev.button == 1:
                    first_point = pos

                    if shape.point_exist(pos):
                        first_point = pos
                    else:
                        shape.add_point(pos, False)
                        first_point = None
                    shape.generate_mesh()
                elif ev.button == 2:
                    if shape.point_exist(pos):
                        first_point = pos
                        creating_line = True
                elif ev.button == 3:
                    if shape.point_exist(pos):
                        shape.del_point(pos)
                        shape.generate_mesh()
            elif ev.type == pg.MOUSEBUTTONUP:
                pos = round_tuple(ev.pos)
                if ev.button == 1:
                    if pos == first_point:
                        shape.set_point(pos, not shape.get_point_anchored(pos), False)
                    elif first_point:
                        if not shape.point_exist(pos):
                            shape.set_point(pos, False)
                        shape.add_stick(first_point, pos)
                    shape.generate_mesh()
                elif ev.button == 2:
                    if creating_line and shape.point_exist(pos) and pos != first_point:
                        shape.add_stick(first_point, pos)
                        shape.generate_mesh()
                    creating_line = False
                    first_point = None

            elif ev.type == pg.KEYDOWN:
                if ev.unicode == " ":
                    editing = not editing
                    shape.generate_mesh()
                    print(shape.serialize())
    else:
        for ev in pg.event.get():
            if ev.type == pg.QUIT:
                done = True
            elif ev.type == pg.KEYDOWN:
                if ev.unicode == " ":
                    editing = not editing
                    shape.generate_mesh()

    display.fill((0, 0, 0))

    for stick in shape.sticks_set:
        draw_stick(display, stick)

    for point in shape.points_set:
        draw_point(display, point)

    pg.display.update()
    if not editing:
        shape.emulate(10)
    clock.tick(fps)
