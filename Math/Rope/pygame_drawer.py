from .objects import *
import pygame as pg

DRAW_COLOR = (255, 255, 255)
GHOST_DRAW_COLOR = (100, 100, 100)
ANCHORED_POINT_COLOR = (255, 0, 0)
DRAW_POINT_SIZE = 5
POINT_DECORATOR_SIZE = 7


def draw_point(surf: pg.Surface, point: Point, offset: pg.Vector2 = None):
    offset = offset if offset else pg.Vector2()
    if point.anchored:
        pg.draw.circle(surf, ANCHORED_POINT_COLOR, point.pos+offset, DRAW_POINT_SIZE)
        pg.draw.circle(surf, DRAW_COLOR, point.pos+offset, POINT_DECORATOR_SIZE, width=1)
    else:
        pg.draw.circle(surf, DRAW_COLOR, point.pos+offset, DRAW_POINT_SIZE)
        pg.draw.circle(surf, DRAW_COLOR, point.pos+offset, POINT_DECORATOR_SIZE, width=1)


def draw_stick(surf: pg.Surface, line: Stick, offset: pg.Vector2 = None):
    offset = offset if offset else pg.Vector2()
    pg.draw.line(surf, DRAW_COLOR, line.point1.pos+offset, line.point2.pos+offset)


def draw_ghost_point(surf, pos: pg.Vector2, offset: pg.Vector2 = None):
    offset = offset if offset else pg.Vector2()
    pg.draw.circle(surf, GHOST_DRAW_COLOR, pos+offset, DRAW_POINT_SIZE)
    pg.draw.circle(surf, GHOST_DRAW_COLOR, pos+offset, POINT_DECORATOR_SIZE, width=1)


__all__ = [
    "draw_point",
    "draw_stick",
    "draw_ghost_point"
]
