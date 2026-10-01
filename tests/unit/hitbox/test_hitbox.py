import math
import random

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

    # 45 degrees turns the axis-aligned edges into diagonals
    rot.scale = (1.0, 1.0)
    rot.angle = 45.0
    diagonals = {(0.707107, 0.707107), (0.707107, -0.707107)}
    directions = _axis_directions(rot._get_axes())
    assert diagonals <= directions
    # and the diagonals into axis-aligned edges. Whether those are skipped
    # depends on the platform's sin() and cos(): sin(pi / 4) is
    # 0.7071067811865476 on Windows but 0.7071067811865475 on Linux, so the
    # rotated normals may be off axis by ~1e-16 and still get tested.
    assert directions - diagonals <= {(1.0, 0.0), (0.0, 1.0), (0.0, -1.0)}

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


def test_radius():
    """The radius is the distance from the position to the farthest point"""
    hb = hitbox.HitBox(points)  # (0, 0) to (10, 10), so (10, 10) is farthest
    assert hb._get_radius() == pytest.approx(200**0.5, rel=1e-5)
    # Never smaller than the true distance, so rounding can't cause misses
    assert hb._get_radius() >= 200**0.5

    # Cached, and not changed by moving
    radius = hb._get_radius()
    assert hb._radius == radius
    hb.position = (100.0, -50.0)
    assert hb._get_radius() == radius

    # Recalculated when the scale changes, including negative scales
    hb.scale = (2.0, -0.5)
    assert hb._radius is None
    assert hb._get_radius() == pytest.approx((20**2 + 5**2) ** 0.5, rel=1e-5)


def test_radius_rotatable():
    """Rotation doesn't change the radius"""
    rot = hitbox.HitBox(octagon).create_rotatable()
    radius = rot._get_radius()
    assert radius == pytest.approx(20**0.5, rel=1e-5)
    for angle in (30.0, 45.0, 90.0, 217.0):
        rot.angle = angle
        assert rot._get_radius() == radius
        farthest = max(
            ((x - rot.position[0]) ** 2 + (y - rot.position[1]) ** 2) ** 0.5
            for x, y in rot.get_adjusted_points()
        )
        assert farthest <= radius


def test_radius_empty():
    assert hitbox.HitBox([])._get_radius() == pytest.approx(0.0, abs=1e-5)


def test_radius_subclass_override():
    """The radius comes from get_adjusted_points() if a subclass overrides it."""

    class StretchedHitBox(hitbox.HitBox):
        def get_adjusted_points(self):
            px, py = self.position
            return [(x * 3 + px, y + py) for x, y in self.points]

    hb = StretchedHitBox(points, position=(5.0, 5.0))
    assert hb._get_radius() == pytest.approx((30**2 + 10**2) ** 0.5, rel=1e-5)


def test_radius_covers_rounding():
    """Rounding in the adjusted points must never put a point outside the radius"""
    rng = random.Random(0)
    for _ in range(2000):
        pts = [(rng.uniform(-60, 60), rng.uniform(-60, 60)) for _ in range(rng.randint(3, 8))]
        rot = hitbox.HitBox(pts).create_rotatable(angle=rng.uniform(0, 360))
        rot.scale = (rng.uniform(-3, 3), rng.uniform(-3, 3))
        far = rng.choice([1.0, 1e3, 1e5, 1e7])
        rot.position = (rng.uniform(-far, far), rng.uniform(-far, far))

        radius = rot._get_radius()
        px, py = rot.position
        for x, y in rot.get_adjusted_points():
            assert math.hypot(x - px, y - py) <= radius
