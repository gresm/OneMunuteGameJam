from pathlib import Path
import json as js
from typing import Tuple, Dict, Set


class Level:
    def __init__(self, player_spawn: Tuple[int, int], end_point: Tuple[int, int],
                 base_shape: Tuple[
                     Dict[Tuple[float, float], bool], Dict[Tuple[float, float], Set[Tuple[float, float]]],
                     Dict[Tuple[Tuple[float, float], Tuple[float, float]], float]],
                 max_length: float, max_points: int, max_sticks: int, locked_points: Set[Tuple[float, float]]):
        self.player_spawn = player_spawn
        self.end_point = end_point
        self.base_shape = base_shape
        self.max_length = max_length
        self.max_points = max_points
        self.max_sticks = max_sticks
        self.locked_points = locked_points

    @staticmethod
    def _set_to_dict(st: set):
        ret = {}
        cnt = 0
        for v in st:
            ret[str(cnt)] = v
        return ret

    @staticmethod
    def _dict_to_set(dc: dict):
        return set(dc.values())

    @classmethod
    def _fix_base_shape(cls, bs):
        f: Dict[str, bool] = bs[0]
        s: Dict[str, Dict[str, Tuple[int, int]]] = bs[1]
        t: Dict[str, float] = bs[2]

        fr = {}
        sr = {}
        tr = {}

        for i in f:
            fr[tuple((float(e) for e in i.split()))] = f[i]

        for i in s:
            sr[tuple((float(e) for e in i.split()))] = cls._dict_to_set(s[i])

        for i in t:
            tr[tuple((float(e) for e in i.split()))] = t[i]
        return fr, sr, tr

    def _get_correct_base_shape(self):
        f = self.base_shape[0]
        s = self.base_shape[1]
        t = self.base_shape[2]

        fr: dict = {}
        sr = {}
        tr = {}

        for i in f:
            fr[f"{i[0]} {i[1]}"] = f[i]

        for i in s:
            sr[f"{i[0]} {i[1]}"] = self._set_to_dict(s[i])

        for i in t:
            tr[f"{i[0][0]} {i[0][1]} {i[1][0]} {i[1][1]}"] = t[i]

        return fr, sr, tr

    def serialize(self):
        return {"spawn": self.player_spawn, "end": self.end_point, "level": self._get_correct_base_shape(),
                "max_length": self.max_length, "max_points": self.max_points, "max_sticks": self.max_sticks,
                "locked_points": self._set_to_dict(self.locked_points)}

    @classmethod
    def deserialize(cls, data: dict):
        spawn = data["spawn"]
        end = data["end"]
        level = cls._fix_base_shape(data["level"])
        max_length = data["max_length"]
        max_points = data["max_points"]
        max_sticks = data["max_sticks"]
        locked_points = cls._dict_to_set(data["locked_points"])
        # noinspection PyTypeChecker
        return cls(spawn, end, level, max_length, max_points, max_sticks, locked_points)


def get_path(name: str):
    return Path("Levels") / (name + ".json")


def read_level(name: str):
    with open(get_path(name)) as f:
        return f.read()


def load_level_json(name: str):
    return js.loads(read_level(name))


def load_level(name: str):
    return Level.deserialize(load_level_json(name))
