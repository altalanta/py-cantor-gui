from __future__ import annotations

import math

from cantor_gui.renderers.cantor_dust import cantor_dust_points
from cantor_gui.renderers.cantor_line import cantor_line_segments


def test_line_depth0_one_segment():
    segs = cantor_line_segments(0)
    assert len(segs) == 1
    s, L = segs[0]
    assert math.isclose(L, 1.0)
    assert 0.0 <= s <= 1.0


def test_line_count_and_length():
    for n in range(0, 8):
        segs = cantor_line_segments(n)
        assert len(segs) == 2 ** n
        if segs:
            # All final segments have length (1/3)^n
            expected = (1.0 / 3.0) ** n
            for s, L in segs:
                assert math.isclose(L, expected)
                assert 0.0 <= s <= 1.0
                assert 0.0 <= s + L <= 1.0000001


def test_dust_depth0_one_point():
    pts = cantor_dust_points(0)
    assert len(pts) == 1
    x, y = pts[0]
    assert math.isclose(x, 0.0)
    assert math.isclose(y, 0.0)


def test_dust_counts_and_bounds():
    for n in range(0, 6):
        pts = cantor_dust_points(n)
        assert len(pts) == 4 ** n
        for x, y in pts:
            assert 0.0 <= x <= 1.0
            assert 0.0 <= y <= 1.0

