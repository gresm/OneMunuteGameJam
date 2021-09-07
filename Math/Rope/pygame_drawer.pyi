from Math import Point, Stick
import pygame as pg


def draw_point(surf: pg.Surface, point: Point, offset: pg.Vector2 = None): ...


def draw_stick(surf: pg.Surface, line: Stick, offset: pg.Vector2 = None): ...


def draw_ghost_point(surf: pg.Surface, pos: pg.Vector2, offset: pg.Vector2 = None): ...


def draw_kill_point(surf: pg.Surface, point: Point, offset: pg.Vector2 = None): ...


def draw_kill_stick(surf: pg.Surface, stick: Stick, offset: pg.Vector2 = None): ...
