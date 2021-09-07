from typing import Tuple
import sys

import pygame as pg
from Math import GravityPool, draw_stick, draw_point, draw_kill_stick, draw_kill_point
from levels import Level, save_level, load_level

shape = GravityPool()
kill_shape = GravityPool()

shape.generate_mesh()
kill_shape.generate_mesh()

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
drawing_death = False


def round_tuple(tup: Tuple[int, int]):
    v1 = tup[0] + 12.5 + camera_offset.x
    v2 = tup[1] + 12.5 + camera_offset.y
    return v1 - v1 % 25, v2 - v2 % 25


def get_level(name: str):
    global shape, kill_shape
    loaded_level = load_level(name)
    shape = GravityPool.deserialize(loaded_level.base_shape)
    shape.generate_mesh()

    kill_shape = GravityPool.deserialize(loaded_level.kill_shape)
    kill_shape.generate_mesh()


if len(sys.argv) > 1:
    get_level(sys.argv[1])


while not done:
    if editing:
        for ev in pg.event.get():
            if ev.type == pg.QUIT:
                done = True
            elif ev.type == pg.MOUSEBUTTONDOWN:
                pos = round_tuple(ev.pos)
                if ev.button == 1:
                    first_point = pos
                    
                    if drawing_death:
                        if kill_shape.point_exist(pos):
                            first_point = pos
                        else:
                            kill_shape.add_point(pos, False)
                            first_point = None
                    else:
                        if shape.point_exist(pos):
                            first_point = pos
                        else:
                            shape.add_point(pos, False)
                            first_point = None
                    shape.generate_mesh()
                    kill_shape.generate_mesh()
                elif ev.button == 2:
                    print("pos: ", pos)
                elif ev.button == 3:
                    if drawing_death:
                        if kill_shape.point_exist(pos):
                            kill_shape.del_point(pos)
                            kill_shape.generate_mesh()
                    else:
                        if shape.point_exist(pos):
                            shape.del_point(pos)
                            shape.generate_mesh()
            elif ev.type == pg.MOUSEBUTTONUP:
                pos = round_tuple(ev.pos)
                if ev.button == 1:
                    if drawing_death:
                        if pos == first_point:
                            kill_shape.set_point(pos, not kill_shape.get_point_anchored(pos), False)
                        elif first_point:
                            if not kill_shape.point_exist(pos):
                                kill_shape.set_point(pos, False)
                            kill_shape.add_stick(first_point, pos)
                    else:
                        if pos == first_point:
                            shape.set_point(pos, not shape.get_point_anchored(pos), False)
                        elif first_point:
                            if not shape.point_exist(pos):
                                shape.set_point(pos, False)
                            shape.add_stick(first_point, pos)
                    shape.generate_mesh()
                    kill_shape.generate_mesh()

            elif ev.type == pg.KEYDOWN:
                if ev.unicode == " ":
                    editing = not editing
                    shape.generate_mesh()
                    kill_shape.generate_mesh()
                elif ev.unicode == "k":
                    drawing_death = not drawing_death
                elif ev.unicode == "s":
                    pg.quit()
                    level_name = input("level name: ")
                    player_x = int(input("player x: "))
                    player_y = int(input("player y: "))
                    exit_x = int(input("goal x: "))
                    exit_y = int(input("goal y: "))
                    max_length = float(input("max line size: "))
                    max_points = int(input("max placeable points: "))
                    shape.generate_mesh()
                    kill_shape.generate_mesh()
                    level = Level((player_x, player_y), (exit_x, exit_y), shape.serialize(), max_length, max_points,
                                  -1, shape.points_set, kill_shape.serialize())
                    save_level(level_name, level)
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
                    kill_shape.generate_mesh()

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

    for kill_stick in kill_shape.sticks_set:
        draw_kill_stick(display, kill_stick, camera_offset)

    for kill_point in kill_shape.points_set:
        draw_kill_point(display, kill_point, camera_offset)

    pg.display.update()
    if not editing:
        shape.emulate(10)
        kill_shape.emulate(10)
    clock.tick(fps)

pg.quit()
quit()
