from typing import Dict, Tuple, Set

import pygame as pg


class Point:
    def __init__(self, pos: pg.Vector2, anchored: bool):
        self.pos = pos
        self.vel = pg.Vector2
        self.anchored = anchored

    def __hash__(self):
        return hash(id(self))


class Stick:
    def __init__(self, point1: Point, point2: Point, length: float):
        self.point1 = point1
        self.point2 = point2
        self.length = length

    def correct_pos(self):
        current_diff = self.point2.pos - self.point1.pos
        current_length = current_diff.length()
        current_way = current_diff / current_length

        if current_length == self.length:  # there is no point for extra calculations
            return

        if self.point1.anchored and self.point2.anchored:
            # for some reason we have incorrect size of completely anchored stick
            self.length = current_length
            return

        if self.point1.anchored:
            self.point2.pos = self.point1.pos + current_way * self.length
        elif self.point2.anchored:
            self.point1.pos = self.point2.pos + current_way * self.length * -1
        else:
            line_center = current_way * current_length / 2
            self.point2.pos = self.point1.pos + current_way * self.length
            self.point2 += line_center
            self.point1.pos = self.point2.pos + current_way * self.length * -1
            self.point1 -= line_center

    def __hash__(self):
        return hash(id(self))


class ObjectsPool:
    def __init__(self):
        # dict of points
        # key - position
        # value - Point object
        self._points_dict: Dict[Tuple[float, float], Point] = {}

        # dict of point references
        # fast checking if connected points to that point
        # key - position
        # value - list of positions
        self._points_reference_dict: Dict[Tuple[float, float], Set[Tuple[float, float]]] = {}

        # dict of sticks
        # key - tuple of sticks endpoints
        # value - Stick object
        self._sticks_dict: Dict[Tuple[Tuple[float, float], Tuple[float, float]], Stick] = {}

        # set of points
        # element - Point object
        self._points_set: Set[Point] = set()

        # set of sticks
        # element - Stick object
        self._sticks_set: Set[Stick] = set()

        # determines if mesh was generated
        # value - bool
        self.generated = False

    @staticmethod
    def calculate_point_movement(point: Point):
        pass

    def generate_mesh(self):
        """
        Generates mesh for animation
        :return:
        """
        # clear generated status
        self.generated = False

        # remove old mesh
        self._sticks_set.clear()

        # add sticks from dict
        self._sticks_set.update(self._sticks_dict.values())
        # add points from dict
        # useful for adding movement for points
        self._points_set.update(self._points_dict.values())

        # now we know that there are not any duplicates

        # info if was generated
        self.generated = True

    def emulate(self):
        """
        run physics frame
        :return:
        """
        if not self.generated:  # mesh wasn't generated
            return

        for point in self._points_set:
            if not point.anchored:
                self.calculate_point_movement(point)

        for stick in self._sticks_set:
            stick.correct_pos()

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

        self._points_dict[pos] = Point(pg.Vector2(pos), anchored)
        self._points_reference_dict[pos] = set()
        return True

    def add_stick(self, pos1: Tuple[float, float], pos2: Tuple[float, float], length: float) -> bool:
        """
        Add point to shape
        :param pos1: point1 pos
        :param pos2: point2 pos
        :param length: stick length
        :return: true if creation was successful else false
        """
        pos1, pos2 = self.sort_points(pos1, pos2)
        
        if pos1 not in self._points_dict or pos2 not in self._points_dict:
            # there are no points at given places
            return False

        if tuple(sorted([pos1, pos2])) in self._sticks_dict:
            # stick already exist
            return False

        # add stick to stick dict
        self._sticks_dict[(pos1, pos2)] = Stick(self._points_dict[pos1], self._points_dict[pos2], length)

        # add point reference
        self._points_reference_dict[pos1].add(pos2)
        self._points_reference_dict[pos2].add(pos1)

    def del_point(self, pos: Tuple[float, float]) -> bool:
        if pos not in self._points_dict:
            return False

        del self._points_dict[pos]

        for point in self._points_reference_dict[pos]:
            if not self.del_stick(pos, point):
                return False

        return True

    def del_stick(self, pos1: Tuple[float, float], pos2: Tuple[float, float]):
        pos1, pos2 = self.sort_points(pos1, pos2)
        if (pos1, pos2) not in self._sticks_dict:
            return False

        del self._sticks_dict[(pos1, pos2)]

        self._points_reference_dict[pos1].remove(pos2)
        self._points_reference_dict[pos2].remove(pos1)

    @staticmethod
    def sort_points(point1: Tuple[float, float], point2: Tuple[float, float]):
        return min(point1, point2), max(point1, point2)


__all__ = [
    "Point",
    "Stick",
    "ObjectsPool"
]

del pg
