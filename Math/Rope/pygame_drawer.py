from .objects import *
import pygame as pg

DRAW_COLOR = (255, 255, 255)
ANCHORED_POINT_COLOR = (255, 0, 0)
DRAW_POINT_SIZE = 5
POINT_DECORATOR_SIZE = 7


def draw_point(surf: pg.Surface, point: Point):
    if point.anchored:
        pg.draw.circle(surf, ANCHORED_POINT_COLOR, point.pos, DRAW_POINT_SIZE)
        pg.draw.circle(surf, DRAW_COLOR, point.pos, POINT_DECORATOR_SIZE, width=1)
    else:
        pg.draw.circle(surf, DRAW_COLOR, point.pos, DRAW_POINT_SIZE)
        pg.draw.circle(surf, DRAW_COLOR, point.pos, POINT_DECORATOR_SIZE, width=1)


def draw_stick(surf: pg.Surface, line: Stick):
    pg.draw.line(surf, DRAW_COLOR, line.point1.pos, line.point2.pos)


__all__ = [
    "draw_point",
    "draw_stick"
]
