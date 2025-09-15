from __future__ import annotations

from itertools import product
from typing import Iterable, List, Tuple

from PySide6.QtCore import QRectF
from PySide6.QtGui import QPainterPath


Point = Tuple[float, float]


def cantor_dust_points(depth: int) -> List[Point]:
    """Generate points of the 2D Cantor dust at given depth.

    Constructed as the Cartesian product of the 1D Cantor set with itself.
    Points are derived from base-3 digits of length n with digits in {0,2}.

    For depth n there are 4^n points. Complexity: O(4^n) time and space.
    """
    if depth < 0:
        raise ValueError("depth must be >= 0")
    if depth == 0:
        return [(0.0, 0.0)]

    digits = [0.0, 2.0]
    scale = 1.0 / 3.0
    points: List[Point] = []
    # Generate all base-3 strings of length depth with digits 0 or 2
    for dx in product(digits, repeat=depth):
        x = 0.0
        for i, d in enumerate(dx):
            x += d * (scale ** (i + 1))
        for dy in product(digits, repeat=depth):
            y = 0.0
            for j, d2 in enumerate(dy):
                y += d2 * (scale ** (j + 1))
            points.append((x, y))
    return points


def points_to_rects_path(
    points: Iterable[Point],
    x0: float,
    x1: float,
    y0: float,
    y1: float,
    size: float,
) -> QPainterPath:
    """Pack many tiny squares centered on the points into one QPainterPath.

    Maps [0,1]^2 onto [x0,x1] x [y0,y1]. `size` is the side length in scene units.
    """
    path = QPainterPath()
    sx = (x1 - x0)
    sy = (y1 - y0)
    half = size / 2.0
    for x, y in points:
        cx = x0 + x * sx
        cy = y0 + y * sy
        rect = QRectF(cx - half, cy - half, size, size)
        path.addRect(rect)
    return path

