from typing import Tuple, Optional

import levels as lv
import pygame as pg
from Math import GravityPool, PoolStickIterator, drawer
from player import Player

points_grid = 25


def round_pos(vec: pg.Vector2):
    v = vec + pg.Vector2(points_grid / 2)
    return v - pg.Vector2(v.x % points_grid, v.y % points_grid)


class LevelGenerated(pg.sprite.Sprite):
    camera_speed = 0.05

    def __init__(self, level: lv.Level, image: pg.Surface, operation_steps: int, static_camera: bool = False,
                 player_follow_camera_size: int = 100):
        super().__init__()
        self._image = image
        self.rect = self._image.get_rect()

        self.level = level
        self.spawn = pg.Vector2(self.level.player_spawn)
        self.goal = pg.Vector2(self.level.end_point)
        self.player_rect = pg.Rect(0, 0, 50, 50)
        self.winning_rect = pg.Rect(0, 0, 50, 50)
        self.winning_rect.center = self.goal
        self.goal_rect = pg.Rect(self.goal.x, self.goal.y, 50, 50)
        self.player = Player(self.player_rect, self.spawn)
        self.player_rect.center = self.player.pos
        self.player_group = pg.sprite.Group(self.player)
        self.max_points = self.level.max_points
        self.max_sticks = self.level.max_sticks
        self.max_length = self.level.max_length
        self.pool = GravityPool.deserialize(self.level.base_shape)
        self.kill = GravityPool.deserialize(self.level.kill_shape)

        self.pool.generate_mesh()
        self.kill.generate_mesh()

        self.points_count = 0
        self.building = True

        self.camera = pg.Vector2()
        self.static_camera = static_camera
        self.player_follow_camera_size = player_follow_camera_size
        self.camera_box = pg.Rect(player_follow_camera_size, player_follow_camera_size,
                                  self.rect.width - player_follow_camera_size * 2,
                                  self.rect.height - player_follow_camera_size * 2)

        self.operation_steps: int = operation_steps
        self.selecting: Optional[pg.Vector2] = None

    def _draw_on_surf(self, surf: pg.Surface, offset: pg.Vector2):
        if self.building:
            if self.selecting:
                pg.draw.circle(surf, (255, 255, 255), self.selecting - self.camera, 10, 3)
        pl_rect = self.player_rect.copy()
        pl_rect.center = pg.Vector2(pl_rect.center) - offset

        wn_rect = self.winning_rect.copy()
        wn_rect.center = pg.Vector2(wn_rect.center) - offset

        pg.draw.rect(surf, (255, 255, 255), pl_rect, 3)
        pg.draw.rect(surf, (255, 255, 0), wn_rect, 3)
        for point in self.pool.points_set:
            if self.building or point.anchored:
                drawer.draw_point(surf, point, offset)

        for stick in self.pool.sticks_set:
            drawer.draw_stick(surf, stick, offset)

        for kill_point in self.kill.points_set:
            drawer.draw_kill_point(surf, kill_point, offset)

        for kill_stick in self.kill.sticks_set:
            drawer.draw_kill_stick(surf, kill_stick, offset)

    @property
    def image(self):
        img = self._image.copy()
        self._draw_on_surf(img, self.camera)
        return img

    def update(self, *args, **kwargs) -> None:
        if "setting_steps" in kwargs and kwargs["setting_steps"]:
            if "steps" in kwargs:
                self.operation_steps = kwargs["steps"]
        else:
            self.update_camera()
            self.pool.emulate(self.operation_steps)
            self.kill.emulate(self.operation_steps)
            self.player.update(walls=PoolStickIterator(self.pool))

    def update_camera(self):
        if self.static_camera:
            return

        relative_pos = self.player.pos - self.camera
        player_rect = self.player_rect.copy()
        player_rect.center = relative_pos

        if self.camera_box.contains(player_rect):
            return

        way = self.player.pos - self.camera - pg.Vector2(self.camera_box.center)
        self.camera += way * self.camera_speed

    def restart(self):
        self.pool.generate_mesh()
        self.points_count = 0
        self.respawn_player()

    def respawn_player(self):
        self.player.kill()
        self.player = Player(self.player_rect, self.spawn)
        self.player_group.add(self.player)

    def can_place(self, pos: Tuple[float, float], start_pos: Tuple[float, float]):
        ret = self.pool.point_exist(start_pos) and self.points_count < self.max_points and \
               (pg.Vector2(pos) - pg.Vector2(start_pos)).length() < self.max_length
        return ret

    def try_place(self, pos: Tuple[float, float], start_pos: Tuple[float, float]):
        if not self.can_place(pos, start_pos):
            return False
        r1 = self.pool.add_point(pos, False)
        if r1:
            self.points_count += 1
        return self.pool.add_stick(pos, start_pos)

    def try_connect(self, pos: Tuple[float, float], start_pos: Tuple[float, float]):
        if not (pg.Vector2(pos) - pg.Vector2(start_pos)).length() < self.max_length:
            return False
        return self.pool.add_stick(pos, start_pos)

    def try_remove(self, pos: Tuple[float, float]):
        if pos in self.level.locked_points or not self.pool.point_exist(pos):
            return False

        ret = self.pool.del_point(pos)
        if ret:
            self.points_count -= 1
        return ret

    def place(self, pos: Tuple[float, float]):
        ret = self.try_place(pos, tuple(self.selecting))
        self.pool.generate_mesh()
        return ret

    def connect(self, pos: Tuple[float, float]):
        ret = self.try_connect(pos, tuple(self.selecting))
        self.pool.generate_mesh()
        return ret

    def remove_point(self, pos: Tuple[float, float]):
        ret = self.try_remove(pos)
        self.pool.generate_mesh()
        return ret

    def is_winning(self):
        return self.player_rect.colliderect(self.winning_rect)

    def is_loosing(self):
        for line in PoolStickIterator(self.kill):
            if self.player_rect.clipline(line):
                return True
        return False

    def correct_placement_pos(self, pos: pg.Vector2):
        if self.selecting is None:
            return pos
        dff = pos - self.selecting
        siz = dff.length()
        if siz > self.max_length:
            ser = dff / siz
            corr = ser * self.max_length
            return self.selecting + corr
        return pos

    def select(self, pos: pg.Vector2, button: int):
        if button == 1:
            # left button
            if self.selecting is None:
                if self.pool.point_exist(tuple(pos)):
                    self.selecting = pos
            else:
                if self.pool.point_exist(tuple(pos)):
                    if self.connect(tuple(pos)):
                        self.selecting = pos
                else:
                    if self.place(tuple(pos)):
                        self.selecting = pos
        elif button == 2:
            # middle button
            if self.pool.point_exist(tuple(pos)):
                self.remove_point(tuple(pos))
                if pos == self.selecting:
                    self.selecting = None
        elif button == 3:
            # right button
            if self.pool.point_exist(tuple(pos)):
                self.selecting = pos
            else:
                self.selecting = None

    def interact(self, pos: pg.Vector2, button: int):
        self.select(round_pos(self.camera + pos), button)
