from typing import Dict, Tuple, Set

import pygame as pg


class Point:
    def __init__(self, pos: pg.Vector2, anchored: bool):
        self.pos = pos
        self.old_pos: pg.Vector2 = pg.Vector2(self.pos)
        self.vel: pg.Vector2 = pg.Vector2()
        self._cached_pos: pg.Vector2 = pg.Vector2(self.pos)
        self.anchored = anchored

    def cache_pos(self):
        self._cached_pos = pg.Vector2(self.pos)

    def set_old_pos(self):
        self.old_pos = pg.Vector2(self._cached_pos)

    def __hash__(self):
        return hash(id(self))

    def __repr__(self):
        return f"<Point({self.pos}, {self.anchored}) at: {id(self)}>"


class Stick:
    def __init__(self, point1: Point, point2: Point, length: float):
        self.point1 = point1
        self.point2 = point2
        self.length = length

    def __hash__(self):
        return hash(id(self))

    def __repr__(self):
        return f"<Stick({self.point1}, {self.point2})>"

    def correct_pos(self):
        self.point1.cache_pos()
        self.point2.cache_pos()

        diff = self.point2.pos - self.point1.pos
        length = diff.length()
        way = diff / length if length else pg.Vector2(1)

        if not self.point1.anchored:
            if length > self.length:
                self.point1.pos += way
            elif length < self.length:
                self.point1.pos -= way

        if not self.point2.anchored:
            if length > self.length:
                self.point2.pos -= way
            elif length < self.length:
                self.point2.pos += way

        self.point1.set_old_pos()
        self.point2.set_old_pos()


class ObjectsPool:
    def __init__(self):
        # dict of points
        # key - position
        # value - is_anchored
        self._points_dict: Dict[Tuple[float, float], bool] = {}

        # dict of point references
        # fast checking if connected points to that point
        # key - position
        # value - list of positions
        self._points_reference_dict: Dict[Tuple[float, float], Set[Tuple[float, float]]] = {}

        # dict of sticks
        # key - tuple of sticks endpoints
        # value - stick length
        self._sticks_dict: Dict[Tuple[Tuple[float, float], Tuple[float, float]], float] = {}

        # set of points
        # element - Point object
        self.points_set: Set[Point] = set()

        # set of sticks
        # element - Stick object
        self.sticks_set: Set[Stick] = set()

        # set of cached points
        # used for generate_mesh() function
        self._cached_points: Dict[Tuple[float, float], Point] = {}

        # set of cached sticks
        # used for generate_mesh() function
        self._cached_sticks: Dict[Tuple[Tuple[float, float], Tuple[float, float]], Stick] = {}

        # determines if mesh was generated
        # value - bool
        self.generated = False

    @staticmethod
    def calculate_point_movement(point: Point):
        pass

    @staticmethod
    def sort_points(point1: Tuple[float, float], point2: Tuple[float, float]):
        return min(point1, point2), max(point1, point2)

    def _make_correct_point(self, pos: Tuple[float, float]) -> Point:
        if pos in self._cached_points:
            return self._cached_points[pos]
        is_anchored = self.get_point_anchored(pos)
        ret = Point(pg.Vector2(pos), is_anchored)
        self._cached_points[pos] = ret
        return ret

    def _make_correct_stick(self, pos1: Tuple[float, float], pos2: Tuple[float, float]):
        pos1, pos2 = self.sort_points(pos1, pos2)

        if (pos1, pos2) in self._cached_sticks:
            return self._cached_sticks[pos1, pos2]

        if pos1 in self._cached_points:
            p1 = self._cached_points[pos1]
        else:
            p1 = self._make_correct_point(pos1)
            self._cached_points[pos1] = p1

        if pos2 in self._cached_points:
            p2 = self._cached_points[pos2]
        else:
            p2 = self._make_correct_point(pos2)
            self._cached_points[pos2] = p2

        ret = Stick(p1, p2, self._sticks_dict[pos1, pos2])
        self._cached_sticks[pos1, pos2] = ret
        return ret

    def _fix_sticks(self, times: int = 1):
        for _ in range(times):
            for stick in self.sticks_set:
                stick.correct_pos()

    def generate_mesh(self):
        """
        Generates mesh for simulation
        :return:
        """
        # clear generated status
        self.generated = False

        # remove old mesh
        self.points_set.clear()
        self.sticks_set.clear()
        self._cached_points.clear()
        self._cached_sticks.clear()

        # add sticks from dict
        for stick in self._sticks_dict:
            self.sticks_set.add(self._make_correct_stick(stick[0], stick[1]))

        # add points from dict
        for point in self._points_dict:
            self.points_set.add(self._make_correct_point(point))

        # now we know that there are not any duplicates

        # info if was generated
        self.generated = True

    def emulate(self, times: int = 1):
        """
        run physics frame
        :return:
        """
        if not self.generated:  # mesh wasn't generated
            return

        for point in self.points_set:
            if not point.anchored:
                self.calculate_point_movement(point)

        self._fix_sticks(times)

    def add_point(self, pos: Tuple[float, float], anchored: bool) -> bool:
        """
        Add point to shape
        :param pos: position
        :param anchored: should point be anchored
        :return: true if creation was successful else false
        """
        if pos in self._points_dict:
            # point already exist
            return False

        self._points_dict[pos] = anchored
        self._points_reference_dict[pos] = set()
        return True

    def add_stick(self, pos1: Tuple[float, float], pos2: Tuple[float, float], length: float = None) -> bool:
        """
        Add point to shape
        :param pos1: point1 pos
        :param pos2: point2 pos
        :param length: stick length
        :return: true if creation was successful else false
        """
        pos1, pos2 = self.sort_points(pos1, pos2)

        if length is None:
            length = (pg.Vector2(pos2) - pg.Vector2(pos1)).length()

        if pos1 not in self._points_dict or pos2 not in self._points_dict:
            # there are no points at given places
            return False

        if (pos1, pos2) in self._sticks_dict:
            # stick already exist
            return False

        # add stick to stick dict
        self._sticks_dict[(pos1, pos2)] = length

        # add point reference
        self._points_reference_dict[pos1].add(pos2)
        self._points_reference_dict[pos2].add(pos1)
        return True

    def del_point(self, pos: Tuple[float, float]) -> bool:
        if pos not in self._points_dict:
            return False

        for point in self._points_reference_dict[pos].copy():
            self.del_stick(pos, point)

        del self._points_dict[pos]

        return True

    def del_stick(self, pos1: Tuple[float, float], pos2: Tuple[float, float]):
        pos1, pos2 = self.sort_points(pos1, pos2)
        if (pos1, pos2) not in self._sticks_dict:
            return False

        del self._sticks_dict[(pos1, pos2)]

        try:
            self._points_reference_dict[pos1].remove(pos2)
        except KeyError:
            pass

        try:
            self._points_reference_dict[pos2].remove(pos1)
        except KeyError:
            pass

        return True

    def point_exist(self, pos: Tuple[float, float]):
        return pos in self._points_dict

    def set_point(self, pos: Tuple[float, float], anchored: bool, restart_references: bool = True):
        self._points_dict[pos] = anchored
        if restart_references:
            self._points_reference_dict[pos] = set()

    def get_point_anchored(self, pos: Tuple[float, float]):
        if self.point_exist(pos):
            return self._points_dict[pos]


class GravityPool(ObjectsPool):
    gravity = pg.Vector2(0, 3)
    max_diff = 100

    @classmethod
    def calculate_point_movement(cls, point: Point):
        diff = point.pos - point.old_pos
        point.pos += cls.gravity
        point.pos += diff

    @classmethod
    def fix_diff(cls, vec: pg.Vector2):
        if vec.length() > cls.max_diff:
            vec = vec / vec.length() * cls.max_diff
        return vec


__all__ = [
    "Point",
    "Stick",
    "ObjectsPool",
    "GravityPool"
]
