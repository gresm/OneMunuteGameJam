from typing import Iterable, Tuple, Union
import pygame as pg

_POS = Union[Tuple[int, int], pg.Vector2]


class Player(pg.sprite.Sprite):
    angular_drag = 0.99
    floor_angular_drag = 0.98
    gravity = pg.Vector2(y=1)
    iterations = 5

    def __init__(self, rect: pg.Rect, pos: pg.Vector2, vel: pg.Vector2 = None):
        super().__init__()
        self.rect = rect
        self.image = pg.Surface(self.rect.size, pg.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        pg.draw.rect(self.image, (255, 255, 255), self.rect, 1)
        self.vel = vel if vel else pg.Vector2()
        self.pos = pos

    def collide_with_walls(self, walls: Iterable[Tuple[_POS, _POS]]):
        end_vel = pg.Vector2()

        for _ in range(self.iterations):
            # noinspection PyShadowingNames
            for line in walls:
                clipped = self.rect.clipline(line)
                if not clipped:  # colliding with nothing
                    continue

                first_diff = self.pos - pg.Vector2(clipped[0])
                second_diff = self.pos - pg.Vector2(clipped[1])
                fixed_diff = first_diff + second_diff
                fixed_len = fixed_diff.length()

                if not fixed_len:  # equals 0
                    continue

                fixed_serialized = fixed_diff / 5

                self.pos += fixed_serialized
                end_vel += fixed_serialized
                end_vel *= self.floor_angular_drag

                self.rect.center = self.pos
                self.vel += end_vel

    def update(self, *args, **kwargs) -> None:
        self.pos += self.vel
        self.rect.center = self.pos
        self.vel *= self.angular_drag

        if "walls" in kwargs:
            self.collide_with_walls(kwargs["walls"])

        self.rect.center = self.pos
        self.vel += self.gravity
