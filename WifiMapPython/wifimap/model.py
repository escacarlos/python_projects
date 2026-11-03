from __future__ import annotations

from dataclasses import asdict, dataclass
import math

import numpy as np


MAX_DIMENSION = 500
MATERIAL_ATTENUATION = {
    "Plaster": 0.3,
    "Wood": 0.5,
    "Brick": 1.0,
    "Cement": 1.33,
    "Reinforced concrete": 1.66,
    "Metal": 2.0,
}


@dataclass
class AccessPoint:
    id: int
    x: int
    y: int
    frequency: float
    power: int


@dataclass
class Barrier:
    id: int
    x1: int
    y1: int
    x2: int
    y2: int
    thickness: int
    material: str

    @property
    def horizontal(self) -> bool:
        return self.y1 == self.y2


class MapModel:
    """Map data and vectorized signal propagation, independent of Qt."""

    def __init__(self, length: int = 50, width: int = 50) -> None:
        self._validate_dimensions(length, width)
        self.length = length
        self.width = width
        self.access_points: list[AccessPoint] = []
        self.barriers: list[Barrier] = []
        self._next_id = 1
        self._signal_cache: np.ndarray | None = None

    @staticmethod
    def _validate_dimensions(length: int, width: int) -> None:
        if not (1 <= length <= MAX_DIMENSION and 1 <= width <= MAX_DIMENSION):
            raise ValueError(f"Map dimensions must be between 1 and {MAX_DIMENSION}.")

    def _changed(self) -> None:
        self._signal_cache = None

    def _coordinate(self, x: int, y: int) -> None:
        if not (0 <= x < self.length and 0 <= y < self.width):
            raise ValueError("Coordinates must be inside the map.")

    def _occupied(self, x: int, y: int, except_id: int | None = None) -> bool:
        if any(p.id != except_id and p.x == x and p.y == y for p in self.access_points):
            return True
        return any(
            b.id != except_id
            and min(b.x1, b.x2) <= x <= max(b.x1, b.x2)
            and min(b.y1, b.y2) <= y <= max(b.y1, b.y2)
            for b in self.barriers
        )

    def add_access_point(self, x: int, y: int, frequency: float, power: int) -> AccessPoint:
        self._coordinate(x, y)
        self._validate_radio(frequency, power)
        if self._occupied(x, y):
            raise ValueError("That location is already occupied.")
        point = AccessPoint(self._next_id, x, y, float(frequency), int(power))
        self._next_id += 1
        self.access_points.append(point)
        self._changed()
        return point

    def update_access_point(
        self, point_id: int, x: int, y: int, frequency: float, power: int
    ) -> None:
        point = self._find(self.access_points, point_id, "Access point")
        self._coordinate(x, y)
        self._validate_radio(frequency, power)
        if self._occupied(x, y, except_id=point_id):
            raise ValueError("That location is already occupied.")
        point.x, point.y = x, y
        point.frequency, point.power = float(frequency), int(power)
        self._changed()

    @staticmethod
    def _validate_radio(frequency: float, power: int) -> None:
        if frequency not in (2.4, 5.0):
            raise ValueError("Frequency must be 2.4 or 5.0 GHz.")
        if not 11 <= power <= 20:
            raise ValueError("Transmit power must be between 11 and 20 dBm.")

    def add_barrier(
        self, x1: int, y1: int, x2: int, y2: int, thickness: int, material: str
    ) -> Barrier:
        self._validate_barrier(x1, y1, x2, y2, thickness, material)
        if any(p.x == x1 == x2 and min(y1, y2) <= p.y <= max(y1, y2)
               or p.y == y1 == y2 and min(x1, x2) <= p.x <= max(x1, x2)
               for p in self.access_points):
            raise ValueError("A barrier cannot pass through an access point.")
        barrier = Barrier(self._next_id, x1, y1, x2, y2, thickness, material)
        self._next_id += 1
        self.barriers.append(barrier)
        self._changed()
        return barrier

    def update_barrier(
        self,
        barrier_id: int,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        thickness: int,
        material: str,
    ) -> None:
        barrier = self._find(self.barriers, barrier_id, "Barrier")
        self._validate_barrier(x1, y1, x2, y2, thickness, material)
        if any(p.x == x1 == x2 and min(y1, y2) <= p.y <= max(y1, y2)
               or p.y == y1 == y2 and min(x1, x2) <= p.x <= max(x1, x2)
               for p in self.access_points):
            raise ValueError("A barrier cannot pass through an access point.")
        barrier.x1, barrier.y1, barrier.x2, barrier.y2 = x1, y1, x2, y2
        barrier.thickness, barrier.material = thickness, material
        self._changed()

    def _validate_barrier(
        self, x1: int, y1: int, x2: int, y2: int, thickness: int, material: str
    ) -> None:
        self._coordinate(x1, y1)
        self._coordinate(x2, y2)
        if (x1 != x2 and y1 != y2) or (x1 == x2 and y1 == y2):
            raise ValueError("A barrier must be a non-zero-length horizontal or vertical line.")
        if not 1 <= thickness <= 60:
            raise ValueError("Barrier thickness must be between 1 and 60.")
        if material not in MATERIAL_ATTENUATION:
            raise ValueError("Unknown barrier material.")

    @staticmethod
    def _find(items: list, item_id: int, kind: str):
        for item in items:
            if item.id == item_id:
                return item
        raise ValueError(f"{kind} no longer exists.")

    def remove(self, item_id: int) -> None:
        for items in (self.access_points, self.barriers):
            for index, item in enumerate(items):
                if item.id == item_id:
                    del items[index]
                    self._changed()
                    return
        raise ValueError("Selected element no longer exists.")

    def resize(self, length: int, width: int, preserve_elements: bool = True) -> None:
        self._validate_dimensions(length, width)
        if preserve_elements and any(
            p.x >= length or p.y >= width for p in self.access_points
        ):
            raise ValueError("An access point would be outside the resized map.")
        if preserve_elements and any(
            b.x1 >= length or b.x2 >= length or b.y1 >= width or b.y2 >= width
            for b in self.barriers
        ):
            raise ValueError("A barrier would be outside the resized map.")
        self.length, self.width = length, width
        if not preserve_elements:
            self.access_points.clear()
            self.barriers.clear()
        self._changed()

    @property
    def signal(self) -> np.ndarray:
        if self._signal_cache is None:
            self._signal_cache = self.calculate_signal()
        return self._signal_cache

    def calculate_signal(self) -> np.ndarray:
        xs, ys = np.ogrid[: self.length, : self.width]
        best = np.full((self.length, self.width), -100.0, dtype=np.float32)
        for point in self.access_points:
            dx = xs - point.x
            dy = ys - point.y
            distance = np.maximum(np.sqrt(dx * dx + dy * dy), 1.0)
            wavelength = 0.125 if point.frequency == 2.4 else 0.06
            signal = point.power + 20.0 * np.log10(wavelength / (4.0 * math.pi * distance))
            for barrier in self.barriers:
                crosses = self._crosses_barrier(point, xs, ys, barrier)
                signal = signal - crosses * int(
                    barrier.thickness * MATERIAL_ATTENUATION[barrier.material]
                )
            np.maximum(best, signal, out=best)
        return best

    @staticmethod
    def _crosses_barrier(
        point: AccessPoint, xs: np.ndarray, ys: np.ndarray, barrier: Barrier
    ) -> np.ndarray:
        # A barrier is a finite axis-aligned segment; broadcast each cell test.
        if barrier.horizontal:
            line_y = barrier.y1
            denominator = ys - point.y
            t = np.divide(
                line_y - point.y,
                denominator,
                out=np.full((1, ys.shape[1]), np.inf, dtype=float),
                where=denominator != 0,
            )
            with np.errstate(invalid="ignore"):
                cross_x = point.x + t * (xs - point.x)
            return (
                (denominator != 0)
                & (t >= 0)
                & (t <= 1)
                & (cross_x >= min(barrier.x1, barrier.x2))
                & (cross_x <= max(barrier.x1, barrier.x2))
            )
        line_x = barrier.x1
        denominator = xs - point.x
        t = np.divide(
            line_x - point.x,
            denominator,
            out=np.full((xs.shape[0], 1), np.inf, dtype=float),
            where=denominator != 0,
        )
        with np.errstate(invalid="ignore"):
            cross_y = point.y + t * (ys - point.y)
        return (
            (denominator != 0)
            & (t >= 0)
            & (t <= 1)
            & (cross_y >= min(barrier.y1, barrier.y2))
            & (cross_y <= max(barrier.y1, barrier.y2))
        )

    def to_dict(self) -> dict:
        return {
            "format": "wifimap",
            "version": 1,
            "length": self.length,
            "width": self.width,
            "access_points": [asdict(point) for point in self.access_points],
            "barriers": [asdict(barrier) for barrier in self.barriers],
        }

    @classmethod
    def from_dict(cls, data: dict) -> MapModel:
        if data.get("format") != "wifimap" or data.get("version") != 1:
            raise ValueError("Unsupported or invalid WifiMap file.")
        model = cls(int(data["length"]), int(data["width"]))
        item_ids: set[int] = set()
        for row in data.get("access_points", []):
            point = model.add_access_point(
                int(row["x"]), int(row["y"]), float(row["frequency"]), int(row["power"])
            )
            point_id = int(row.get("id", point.id))
            if point_id < 1 or point_id in item_ids:
                raise ValueError("Map contains invalid or duplicate element IDs.")
            point.id = point_id
            item_ids.add(point_id)
        for row in data.get("barriers", []):
            barrier = model.add_barrier(
                int(row["x1"]), int(row["y1"]), int(row["x2"]), int(row["y2"]),
                int(row["thickness"]), str(row["material"]),
            )
            barrier_id = int(row.get("id", barrier.id))
            if barrier_id < 1 or barrier_id in item_ids:
                raise ValueError("Map contains invalid or duplicate element IDs.")
            barrier.id = barrier_id
            item_ids.add(barrier_id)
        if item_ids:
            model._next_id = max(item_ids) + 1
        return model
