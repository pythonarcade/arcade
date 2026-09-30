import pytest
from arcade import hitbox

points = [(0.0, 0.0), (0.0, 10.0), (10.0, 10.0), (10.0, 0.0)]
rot_90 = [(0.0, 0.0), (10.0, 0), (10.0, -10.0), (0.0, -10.0)]


def test_module():
    # Make sure the module is loaded
    assert hitbox.algo_default
    assert hitbox.algo_detailed
    assert hitbox.algo_simple
    assert hitbox.algo_bounding_box


def test_create():
    hb = hitbox.HitBox(points)
    assert hb.points == points
    assert hb.get_adjusted_points() == points
    assert hb.position == (0.0, 0.0)
    assert hb.scale == (1.0, 1.0)
    assert hb.bottom == 0.0
    assert hb.top == 10.0
    assert hb.left == 0.0
    assert hb.right == 10.0


def test_scale():
    hb = hitbox.HitBox(points)
    hb.scale = (2.0, 2.0)
    assert hb.scale == (2.0, 2.0)
    assert hb.get_adjusted_points() == [(0.0, 0.0), (0.0, 20.0), (20.0, 20.0), (20.0, 0.0)]


def test_position():
    hb = hitbox.HitBox(points)
    hb.position = (10.0, 10.0)
    assert hb.position == (10.0, 10.0)
    assert hb.get_adjusted_points() == [(10.0, 10.0), (10.0, 20.0), (20.0, 20.0), (20.0, 10.0)]


def test_create_rotatable():
    hb = hitbox.HitBox(points)
    rot = hb.create_rotatable()
    assert rot.angle == 0.0
    assert rot.position == (0.0, 0.0)
    rot.angle = 90.0
    assert rot.angle == 90.0

    rot_p = rot.get_adjusted_points()
    for i, (a, b) in enumerate(zip(rot_90, rot_p)):
        assert a == pytest.approx(b, abs=1e-6), f"[{i}] {a} != {b}"


def test_adjusted_bounds():
    hb = hitbox.HitBox(points)
    assert hb.get_adjusted_bounds() == (0.0, 10.0, 0.0, 10.0)
    # Cached while nothing changes
    assert hb.get_adjusted_bounds() is hb.get_adjusted_bounds()

    hb.position = (5.0, -5.0)
    assert hb.get_adjusted_bounds() == (5.0, 15.0, -5.0, 5.0)

    hb.scale = (2.0, -1.0)
    assert hb.get_adjusted_bounds() == (5.0, 25.0, -15.0, -5.0)


def test_adjusted_bounds_rotatable():
    rot = hitbox.HitBox(points).create_rotatable()
    assert rot.get_adjusted_bounds() == (0.0, 10.0, 0.0, 10.0)

    rot.angle = 90.0
    bounds = rot.get_adjusted_bounds()
    assert bounds == pytest.approx((0.0, 10.0, -10.0, 0.0), abs=1e-6)
    assert bounds == pytest.approx((rot.left, rot.right, rot.bottom, rot.top))

    rot.angle = 45.0
    diagonal = 10.0 * 2**0.5
    assert rot.get_adjusted_bounds() == pytest.approx(
        (0.0, diagonal, -diagonal / 2, diagonal / 2), abs=1e-6
    )


def test_adjusted_bounds_subclass_override():
    """Bounds follow get_adjusted_points() even if a subclass overrides it."""

    class ShiftingHitBox(hitbox.HitBox):
        offset = 0.0

        def get_adjusted_points(self):
            return [(x + self.offset, y) for x, y in self.points]

    hb = ShiftingHitBox(points)
    assert hb.get_adjusted_bounds() == (0.0, 10.0, 0.0, 10.0)
    hb.offset = 100.0
    assert hb.get_adjusted_bounds() == (100.0, 110.0, 0.0, 10.0)
