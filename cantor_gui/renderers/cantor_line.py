from __future__ import annotations

from typing import Iterable, List, Tuple

from PySide6.QtGui import QPainterPath, QPen
from PySide6.QtCore import QPointF


Segment = Tuple[float, float]  # (start, length) within [0,1]


def cantor_line_segments(depth: int) -> List[Segment]:
    """Return the final level segments of the Cantor set at given depth.

    Iterative middle-third removal on [0,1]. At depth n there are 2^n segments of
    length (1/3)^n.

    Complexity: O(2^n) time and space.
    """
    if depth < 0:
        raise ValueError("depth must be >= 0")
    segments: List[Segment] = [(0.0, 1.0)]
    for _ in range(depth):
        next_segs: List[Segment] = []
        for s, L in segments:
            third = L / 3.0
            next_segs.append((s, third))
            next_segs.append((s + 2.0 * third, third))
        segments = next_segs
    return segments


def cantor_line_levels(depth: int) -> List[List[Segment]]:
    """Return list of levels 0..depth, each a list of segments (start,length).

    Level 0 is [(0,1)]. Each subsequent level removes the middle third from each
    segment of the previous level.

    Complexity: O(2^(n+1)) total segments generated across all levels.
    """
    if depth < 0:
        raise ValueError("depth must be >= 0")
    levels: List[List[Segment]] = []
    current: List[Segment] = [(0.0, 1.0)]
    levels.append(current)
    for _ in range(depth):
        next_segs: List[Segment] = []
        for s, L in current:
            third = L / 3.0
            next_segs.append((s, third))
            next_segs.append((s + 2.0 * third, third))
        current = next_segs
        levels.append(current)
    return levels


def segments_to_path(
    segments: Iterable[Segment],
    x0: float,
    x1: float,
    y: float,
    thickness: float,
) -> QPainterPath:
    """Pack many horizontal line segments into a single QPainterPath.

    Maps [0,1] along X to [x0,x1] at fixed scene Y. Thickness is used by the pen
    when stroking the path.
    """
    path = QPainterPath()
    scale = (x1 - x0)
    for s, L in segments:
        xs = x0 + s * scale
        xe = xs + L * scale
        path.moveTo(QPointF(xs, y))
        path.lineTo(QPointF(xe, y))
    return path

