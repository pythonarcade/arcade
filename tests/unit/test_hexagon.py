from arcade.hexagon import (
    HexTile,
    Layout,
    OffsetCoord,
    flat_orientation,
    hextile_to_pixel,
    line,
    pixel_to_hextile,
    pointy_orientation,
)
from pyglet.math import Vec2

# TODO: grab the rest of the tests from my main machine


def equal_offset_coord(name, a, b):
    assert a.col == b.col and a.row == b.row


def equal_doubled_coord(name, a, b):
    assert a.col == b.col and a.row == b.row


def test_hex_equality():
    assert HexTile(3, 4, -7) == HexTile(3, 4, -7)
    assert HexTile(3, 4, -7) != HexTile(3, 3, -6)
    assert HexTile(3, 4, -7) != HexTile(0, 0, 0)
    assert HexTile(3, 4, -7) != HexTile(4, -7, 3)


def test_hex_pixel_roundtrip():
    flat = Layout(flat_orientation, Vec2(10.0, 15.0), Vec2(35.0, 71.0))
    pointy = Layout(pointy_orientation, Vec2(10.0, 15.0), Vec2(35.0, 71.0))

    h = HexTile(3, 4, -7)
    assert h == round(pixel_to_hextile(hextile_to_pixel(h, flat), flat))
    assert h == round(pixel_to_hextile(hextile_to_pixel(h, pointy), pointy))


def test_list_of_hexes():
    assert [
        HexTile(0, 0, 0),
        HexTile(0, -1, 1),
        HexTile(0, -2, 2),
    ] == [
        HexTile(0, 0, 0),
        HexTile(0, -1, 1),
        HexTile(0, -2, 2),
    ]

    assert [HexTile(0, 0, 0), HexTile(0, -1, 1)] != [HexTile(0, 0, 0)]

    assert [HexTile(0, 0, 0), HexTile(0, -1, 1)] != [HexTile(0, -1, 1)]

    assert [HexTile(0, 0, 0), HexTile(0, -1, 1)] != [HexTile(0, -1, 1), HexTile(0, 0, 0)]

    assert HexTile(0, 0, 0) in [HexTile(0, 0, 0), HexTile(0, -1, 1)]

    assert HexTile(0, 0, 0) not in [HexTile(0, -1, 1), HexTile(0, -2, 2)]


def test_hex_arithmetic():
    assert HexTile(4, -10, 6) == HexTile(1, -3, 2) + HexTile(3, -7, 4)
    assert HexTile(-2, 4, -2) == HexTile(1, -3, 2) - HexTile(3, -7, 4)


def test_hex_direction():
    assert HexTile(0, -1, 1) == HexTile.direction(2)


def test_hex_neighbor():
    assert HexTile(1, -3, 2) == HexTile(1, -2, 1).neighbor(2)


def test_hex_diagonal():
    assert HexTile(-1, -1, 2) == HexTile(1, -2, 1).diagonal_neighbor(3)


def test_hex_distance():
    assert 7 == HexTile(3, -7, 4).distance_to(HexTile(0, 0, 0))


def test_hex_rotate_right():
    assert HexTile(1, -3, 2).rotate_right() == HexTile(3, -2, -1)


def test_hex_rotate_left():
    assert HexTile(1, -3, 2).rotate_left() == HexTile(-2, -1, 3)


def test_hex_round():
    a = HexTile(0.0, 0.0, 0.0)
    b = HexTile(1.0, -1.0, 0.0)
    c = HexTile(0.0, -1.0, 1.0)
    assert HexTile(5, -10, 5) == round(HexTile(0.0, 0.0, 0.0).lerp_between(HexTile(10.0, -20.0, 10.0), 0.5))
    assert round(a) == round(a.lerp_between(b, 0.499))
    assert round(b) == round(a.lerp_between(b, 0.501))

    assert round(a) == round(
        HexTile(
            a.q * 0.4 + b.q * 0.3 + c.q * 0.3,
            a.r * 0.4 + b.r * 0.3 + c.r * 0.3,
            a.s * 0.4 + b.s * 0.3 + c.s * 0.3,
        )
    )

    assert round(c) == round(
        HexTile(
            a.q * 0.3 + b.q * 0.3 + c.q * 0.4,
            a.r * 0.3 + b.r * 0.3 + c.r * 0.4,
            a.s * 0.3 + b.s * 0.3 + c.s * 0.4,
        )
    )


def test_hex_line_draw():
    assert [
        HexTile(0, 0, 0),
        HexTile(0, -1, 1),
        HexTile(0, -2, 2),
        HexTile(1, -3, 2),
        HexTile(1, -4, 3),
        HexTile(1, -5, 4),
    ] == line(HexTile(0, 0, 0), HexTile(1, -5, 4))


def test_layout():
    h = HexTile(3, 4, -7)
    flat = Layout(flat_orientation, Vec2(10.0, 15.0), Vec2(35.0, 71.0))

    assert h == round(pixel_to_hextile(hextile_to_pixel(h, flat), flat))

    pointy = Layout(pointy_orientation, Vec2(10.0, 15.0), Vec2(35.0, 71.0))
    assert h == round(pixel_to_hextile(hextile_to_pixel(h, pointy), pointy))


def test_offset_roundtrip():
    a = HexTile(3, 4, -7)
    b = OffsetCoord(1, -3)

    assert a == a.to_offset("even-q").to_cube("even-q")

    assert b == b.to_cube("even-q").to_offset("even-q")

    assert a == a.to_offset("odd-q").to_cube("odd-q")

    assert b == b.to_cube("odd-q").to_offset("odd-q")

    assert a == a.to_offset("even-r").to_cube("even-r")

    assert b == b.to_cube("even-r").to_offset("even-r")

    assert a == a.to_offset("odd-r").to_cube("odd-r")

    assert b == b.to_cube("odd-r").to_offset("odd-r")


def test_offset_from_cube():
    assert OffsetCoord(1, 3) == HexTile(1, 2, -3).to_offset("even-q")

    assert OffsetCoord(1, 2) == HexTile(1, 2, -3).to_offset("odd-q")


def test_offset_to_cube():
    assert HexTile(1, 2, -3) == OffsetCoord(1, 3).to_cube("even-q")

    assert HexTile(1, 2, -3) == OffsetCoord(1, 2).to_cube("odd-q")
