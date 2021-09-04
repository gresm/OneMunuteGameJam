from typing import Tuple

import pygame as pg
from Math import GravityPool, draw_stick, draw_point
from levels import Level, save_level

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
camera_offset = pg.Vector2()
right = pg.Vector2(1, 0)
down = pg.Vector2(y=1)


def round_tuple(tup: Tuple[int, int]):
    v1 = tup[0] + 12.5 - camera_offset.x
    v2 = tup[1] + 12.5 - camera_offset.y
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
                    print("pos: ", pos)
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

            elif ev.type == pg.KEYDOWN:
                if ev.unicode == " ":
                    editing = not editing
                    shape.generate_mesh()
                elif ev.unicode == "s":
                    pg.quit()
                    name = input("level name: ")
                    player_x = int(input("player x: "))
                    player_y = int(input("player y: "))
                    exit_x = int(input("goal x: "))
                    exit_y = int(input("goal y: "))
                    max_length = float(input("max line size: "))
                    max_points = int(input("max placeable points: "))
                    shape.generate_mesh()
                    level = Level((player_x, player_y), (exit_x, exit_y), shape.serialize(), max_length, max_points,
                                  -1, shape.points_set)
                    save_level(name, level)
                    done = True
                    quit()
    else:
        for ev in pg.event.get():
            if ev.type == pg.QUIT:
                done = True
            elif ev.type == pg.KEYDOWN:
                if ev.unicode == " ":
                    editing = not editing
                    shape.generate_mesh()

    pressed = pg.key.get_pressed()
    if pressed[pg.K_UP]:
        camera_offset -= down * 6
    if pressed[pg.K_DOWN]:
        camera_offset += down * 6
    if pressed[pg.K_LEFT]:
        camera_offset -= right * 6
    if pressed[pg.K_RIGHT]:
        camera_offset += right * 6

    display.fill((0, 0, 0))

    for stick in shape.sticks_set:
        draw_stick(display, stick, camera_offset)

    for point in shape.points_set:
        draw_point(display, point, camera_offset)

    pg.display.update()
    if not editing:
        shape.emulate(10)
    clock.tick(fps)

pg.quit()
quit()
