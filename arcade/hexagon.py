"""Hexagon utilities.

This module started as the Python implementation of the hexagon utilities
from Red Blob Games.

See: https://www.redblobgames.com/grids/hexagons/

CC0 -- No Rights Reserved
"""

import math
from dataclasses import dataclass
from math import isclose
from typing import Literal, NamedTuple, cast

from pyglet.math import Vec2

_EVEN: Literal[1] = 1
_ODD: Literal[-1] = -1

offset_system = Literal["odd-r", "even-r", "odd-q", "even-q"]


class _Orientation(NamedTuple):
    """Helper class to store forward and inverse matrix for hexagon conversion.

    Also stores the start angle for hexagon corners.
    """

    f0: float
    f1: float
    f2: float
    f3: float
    b0: float
    b1: float
    b2: float
    b3: float
    start_angle: float


pointy_orientation = _Orientation(
    math.sqrt(3.0),
    math.sqrt(3.0) / 2.0,
    0.0,
    3.0 / 2.0,
    math.sqrt(3.0) / 3.0,
    -1.0 / 3.0,
    0.0,
    2.0 / 3.0,
    0.5,
)
flat_orientation = _Orientation(
    3.0 / 2.0,
    0.0,
    math.sqrt(3.0) / 2.0,
    math.sqrt(3.0),
    2.0 / 3.0,
    0.0,
    -1.0 / 3.0,
    math.sqrt(3.0) / 3.0,
    0.0,
)


class Layout(NamedTuple):
    """Helper class to store hexagon layout information."""

    orientation: _Orientation
    size: Vec2
    origin: Vec2


# TODO: should this be a np.array?
# TODO: should this be in rust?
# TODO: should this be cached/memoized?
# TODO: benchmark
@dataclass(frozen=True)
class HexTile:
    """A hexagonal tile in cube coordinates.

    For an introduction to hexagonal grids and cube coordinates, see:
    https://www.redblobgames.com/grids/hexagons/
    """

    q: float
    r: float
    s: float

    def __post_init__(self) -> None:
        """Create a hexagon in cube coordinates."""
        cube_sum = self.q + self.r + self.s
        assert isclose(0, cube_sum, abs_tol=1e-14), f"q + r + s must be 0, is {cube_sum}"

    def __eq__(self, other: object) -> bool:
        """Check if two hexagons are equal."""
        result = self.q == other.q and self.r == other.r and self.s == other.s  # type: ignore[attr-defined]
        assert isinstance(result, bool)
        return result

    def __add__(self, other: "HexTile") -> "HexTile":
        """Add two hexagons."""
        return HexTile(self.q + other.q, self.r + other.r, self.s + other.s)

    def __sub__(self, other: "HexTile") -> "HexTile":
        """Subtract two hexagons."""
        return HexTile(self.q - other.q, self.r - other.r, self.s - other.s)

    def __mul__(self, k: int) -> "HexTile":
        """Multiply a hexagon by a scalar."""
        return HexTile(self.q * k, self.r * k, self.s * k)

    def __neg__(self) -> "HexTile":
        """Negate a hexagon."""
        return HexTile(-self.q, -self.r, -self.s)

    def __round__(self) -> "HexTile":
        """Round a hexagon."""
        qi = round(self.q)
        ri = round(self.r)
        si = round(self.s)
        q_diff = abs(qi - self.q)
        r_diff = abs(ri - self.r)
        s_diff = abs(si - self.s)
        if q_diff > r_diff and q_diff > s_diff:
            qi = -ri - si
        elif r_diff > s_diff:
            ri = -qi - si
        else:
            si = -qi - ri
        return HexTile(qi, ri, si)

    def rotate_left(self) -> "HexTile":
        """Rotate a hexagon to the left."""
        return HexTile(-self.s, -self.q, -self.r)

    def rotate_right(self) -> "HexTile":
        """Rotate a hexagon to the right."""
        return HexTile(-self.r, -self.s, -self.q)

    @staticmethod
    def direction(direction: int) -> "HexTile":
        """Return a relative hexagon in a given direction."""
        hex_directions = [
            HexTile(1, 0, -1),
            HexTile(1, -1, 0),
            HexTile(0, -1, 1),
            HexTile(-1, 0, 1),
            HexTile(-1, 1, 0),
            HexTile(0, 1, -1),
        ]
        return hex_directions[direction]

    def neighbor(self, direction: int) -> "HexTile":
        """Return the neighbor in a given direction."""
        return self + self.direction(direction)

    def neighbors(self) -> list["HexTile"]:
        """Return the neighbors of a hexagon."""
        return [self.neighbor(i) for i in range(6)]

    def diagonal_neighbor(self, direction: int) -> "HexTile":
        """Return the diagonal neighbor in a given direction."""
        hex_diagonals = [
            HexTile(2, -1, -1),
            HexTile(1, -2, 1),
            HexTile(-1, -1, 2),
            HexTile(-2, 1, 1),
            HexTile(-1, 2, -1),
            HexTile(1, 1, -2),
        ]
        return self + hex_diagonals[direction]

    def length(self) -> int:
        """Return the length of a hexagon."""
        return int((abs(self.q) + abs(self.r) + abs(self.s)) // 2)

    def distance_to(self, other: "HexTile") -> float:
        """Return the distance between self and another HexTile."""
        return (self - other).length()

    def line_to(self, other: "HexTile") -> list["HexTile"]:
        """Return a list of hexagons between self and another HexTile."""
        return line(self, other)

    def lerp_between(self, other: "HexTile", t: float) -> "HexTile":
        """Perform a linear interpolation between self and another HexTile."""
        return lerp(self, other, t)

    def to_pixel(self, layout: Layout) -> Vec2:
        """Convert a hexagon to pixel coordinates."""
        return hextile_to_pixel(self, layout)

    def to_offset(self, system: offset_system) -> "OffsetCoord":
        """Convert a hexagon to offset coordinates."""
        if system == "odd-r":
            return roffset_from_cube(self, _ODD)
        if system == "even-r":
            return roffset_from_cube(self, _EVEN)
        if system == "odd-q":
            return qoffset_from_cube(self, _ODD)
        if system == "even-q":
            return qoffset_from_cube(self, _EVEN)

        msg = "system must be odd-r, even-r, odd-q, or even-q"
        raise ValueError(msg)


def lerp(a: HexTile, b: HexTile, t: float) -> HexTile:
    """Perform a linear interpolation between two hexagons."""
    return HexTile(
        a.q * (1.0 - t) + b.q * t,
        a.r * (1.0 - t) + b.r * t,
        a.s * (1.0 - t) + b.s * t,
    )


def distance(a: HexTile, b: HexTile) -> int:
    """Return the distance between two hexagons."""
    return (a - b).length()


def line(a: HexTile, b: HexTile) -> list[HexTile]:
    """Return a list of hexagons between two hexagons."""
    n = distance(a, b)
    # epsilon to nudge points by to falling on an edge
    a_nudge = HexTile(a.q + 1e-06, a.r + 1e-06, a.s - 2e-06)
    b_nudge = HexTile(b.q + 1e-06, b.r + 1e-06, b.s - 2e-06)
    step = 1.0 / max(n, 1)
    return [round(lerp(a_nudge, b_nudge, step * i)) for i in range(n + 1)]


def hextile_to_pixel(h: HexTile, layout: Layout) -> Vec2:
    """Convert axial hexagon coordinates to pixel coordinates."""
    M = layout.orientation  # noqa: N806
    size = layout.size
    origin = layout.origin
    x = (M.f0 * h.q + M.f1 * h.r) * size.x
    y = (M.f2 * h.q + M.f3 * h.r) * size.y
    return Vec2(x + origin.x, y + origin.y)


def pixel_to_hextile(
    p: Vec2,
    layout: Layout,
) -> HexTile:
    """Convert pixel coordinates to cubic hexagon coordinates."""
    M = layout.orientation  # noqa: N806
    size = layout.size
    origin = layout.origin
    pt = Vec2((p.x - origin.x) / size.x, (p.y - origin.y) / size.y)
    q = M.b0 * pt.x + M.b1 * pt.y
    r = M.b2 * pt.x + M.b3 * pt.y
    return HexTile(q, r, -q - r)


def hextile_corner_offset(corner: int, layout: Layout) -> Vec2:
    """Return the offset of a hexagon corner."""
    # Hexagons have 6 corners
    assert 0 <= corner < 6  # noqa: PLR2004
    M = layout.orientation  # noqa: N806
    size = layout.size
    angle = 2.0 * math.pi * (M.start_angle - corner) / 6.0
    return Vec2(size.x * math.cos(angle), size.y * math.sin(angle))


hextile_corners = tuple[Vec2, Vec2, Vec2, Vec2, Vec2, Vec2]


def polygon_corners(h: HexTile, layout: Layout) -> hextile_corners:
    """Return the corners of a hexagon in a list of pixels."""
    corners = []
    center = hextile_to_pixel(h, layout)
    for i in range(6):
        offset = hextile_corner_offset(i, layout)
        corners.append(Vec2(center.x + offset.x, center.y + offset.y))
    result = tuple(corners)
    # Hexagons have 6 corners
    assert len(result) == 6  # noqa: PLR2004
    return cast("hextile_corners", result)


@dataclass(frozen=True)
class OffsetCoord:
    """Offset coordinates."""

    col: float
    row: float

    def to_cube(self, system: offset_system) -> HexTile:
        """Convert offset coordinates to cube coordinates."""
        if system == "odd-r":
            return roffset_to_cube(self, _ODD)
        if system == "even-r":
            return roffset_to_cube(self, _EVEN)
        if system == "odd-q":
            return qoffset_to_cube(self, _ODD)
        if system == "even-q":
            return qoffset_to_cube(self, _EVEN)

        msg = "system must be EVEN (+1) or ODD (-1)"
        raise ValueError(msg)


def qoffset_from_cube(h: HexTile, offset: Literal[-1, 1]) -> OffsetCoord:
    """Convert a hexagon in cube coordinates to q offset coordinates."""
    if offset not in (_EVEN, _ODD):
        msg = "offset must be EVEN (+1) or ODD (-1)"
        raise ValueError(msg)

    col = h.q
    row = h.r + (h.q + offset * (h.q & 1)) // 2  # type: ignore[operator]
    return OffsetCoord(col, row)


def qoffset_to_cube(h: OffsetCoord, offset: Literal[-1, 1]) -> HexTile:
    """Convert a hexagon in q offset coordinates to cube coordinates."""
    if offset not in (_EVEN, _ODD):
        msg = "offset must be EVEN (+1) or ODD (-1)"
        raise ValueError(msg)

    q = h.col
    r = h.row - (h.col + offset * (h.col & 1)) // 2  # type: ignore[operator]
    s = -q - r
    return HexTile(q, r, s)


def roffset_from_cube(h: HexTile, offset: Literal[-1, 1]) -> OffsetCoord:
    """Convert a hexagon in cube coordinates to r offset coordinates."""
    if offset not in (_EVEN, _ODD):
        msg = "offset must be EVEN (+1) or ODD (-1)"
        raise ValueError(msg)

    col = h.q + (h.r + offset * (h.r & 1)) // 2  # type: ignore[operator]
    row = h.r
    return OffsetCoord(col, row)


def roffset_to_cube(h: OffsetCoord, offset: Literal[-1, 1]) -> HexTile:
    """Convert a hexagon in r offset coordinates to cube coordinates."""
    if offset not in (_EVEN, _ODD):
        msg = "offset must be EVEN (+1) or ODD (-1)"
        raise ValueError(msg)

    q = h.col - (h.row + offset * (h.row & 1)) // 2  # type: ignore[operator]
    r = h.row
    s = -q - r
    return HexTile(q, r, s)
