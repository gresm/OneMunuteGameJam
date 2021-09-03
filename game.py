from typing import Tuple

import levels as lv
import pygame as pg
from Math import GravityPool


class LevelGenerated:
    def __init__(self, level: lv.Level):
        self.level = level
        self.spawn = pg.Vector2(self.level.player_spawn)
        self.goal = pg.Vector2(self.level.end_point)
        self.max_points = self.level.max_points
        self.max_sticks = self.level.max_sticks
        self.max_length = self.level.max_length
        self.pool = GravityPool.deserialize(self.level.base_shape)

        self.pool.generate_mesh()

        self.points_count = 0

    def restart(self):
        self.pool.generate_mesh()
        self.points_count = 0

    def can_place(self, pos: Tuple[float, float], start_pos: Tuple[float, float]):
        return self.pool.point_exist(start_pos) and self.points_count > 0 and \
               (pg.Vector2(pos) - pg.Vector2(start_pos)).length() < self.max_length

    def try_place(self, pos: Tuple[float, float], start_pos: Tuple[float, float]):
        if not self.can_place(pos, start_pos):
            return False
        self.points_count += 1
        r1 = self.pool.add_point(pos, False)
        r2 = self.pool.add_stick(pos, start_pos)
        return r1 and r2

    def try_connect(self, pos: Tuple[float, float], start_pos: Tuple[float, float]):
        if not (pg.Vector2(pos) - pg.Vector2(start_pos)).length() < self.max_length:
            return False
        return self.pool.add_stick(pos, start_pos)