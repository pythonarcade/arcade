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


@pytest.mark.parametrize(
    "angle, expected",
    [
        (90.0, [(0.0, 0.0), (10.0, 0.0), (10.0, -10.0), (0.0, -10.0)]),
        (180.0, [(0.0, 0.0), (0.0, -10.0), (-10.0, -10.0), (-10.0, 0.0)]),
        (270.0, [(0.0, 0.0), (-10.0, 0.0), (-10.0, 10.0), (0.0, 10.0)]),
        (-90.0, [(0.0, 0.0), (-10.0, 0.0), (-10.0, 10.0), (0.0, 10.0)]),
        (450.0, [(0.0, 0.0), (10.0, 0.0), (10.0, -10.0), (0.0, -10.0)]),
    ],
)
def test_right_angle_rotation_is_exact(angle, expected):
    """Right angles must not add floating point error to the points"""
    rot = hitbox.HitBox(points).create_rotatable(angle=angle)
    assert rot.get_adjusted_points() == expected


octagon = [(-4.0, -2.0), (-2.0, -4.0), (2.0, -4.0), (4.0, -2.0),
           (4.0, 2.0), (2.0, 4.0), (-2.0, 4.0), (-4.0, 2.0)]  # fmt: skip


def _axis_directions(axes):
    """Unit vectors of the axes, rounded and pointing right, for comparing"""
    result = set()
    for x, y in axes.values():
        length = (x * x + y * y) ** 0.5
        if x < 0:
            x, y = -x, -y
        result.add((round(x / length, 6), round(y / length, 6)))
    return result


def test_axes_skip_axis_aligned_and_duplicate_edges():
    # Every edge of a box is axis-aligned
    assert hitbox.HitBox(points)._get_axes() == {}
    # An octagon's 8 edges only have 2 non axis-aligned directions
    axes = hitbox.HitBox(octagon)._get_axes()
    assert len(axes) == 2
    assert _axis_directions(axes) == {(0.707107, 0.707107), (0.707107, -0.707107)}


def test_axes_follow_scale_and_angle():
    rot = hitbox.HitBox(octagon).create_rotatable()
    axes = rot._get_axes()

    # Moving doesn't change the directions, so the cache is kept
    rot.position = (100.0, 50.0)
    assert rot._get_axes() is axes

    # Non-uniform scale changes the diagonal directions
    rot.scale = (2.0, 1.0)
    assert _axis_directions(rot._get_axes()) == {(0.447214, 0.894427), (0.447214, -0.894427)}

    # 45 degrees turns the diagonals into axis-aligned edges and vice versa
    rot.scale = (1.0, 1.0)
    rot.angle = 45.0
    assert _axis_directions(rot._get_axes()) == {(0.707107, 0.707107), (0.707107, -0.707107)}

    rot.angle = 30.0
    assert len(rot._get_axes()) == 4


def test_axes_subclass_override():
    """Axes come from get_adjusted_points() if a subclass overrides it."""

    class SkewedHitBox(hitbox.HitBox):
        def get_adjusted_points(self):
            return [(x + y, y) for x, y in self.points]

    # The skew turns the box's vertical edges into diagonals
    axes = SkewedHitBox(points)._get_axes()
    assert _axis_directions(axes) == {(0.707107, -0.707107)}
