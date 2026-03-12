import json
import tempfile
from pathlib import Path

import pytest
from arcade import hitbox

points = ((0.0, 0.0), (0.0, 10.0), (10.0, 10.0), (10.0, 0.0))
rot_90 = ((0.0, 0.0), (10.0, 0), (10.0, -10.0), (0.0, -10.0))


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
    assert hb.angle == 0.0
    assert hb.bottom == 0.0
    assert hb.top == 10.0
    assert hb.left == 0.0
    assert hb.right == 10.0


def test_scale():
    hb = hitbox.HitBox(points)
    hb.scale = (2.0, 2.0)
    assert hb.scale == (2.0, 2.0)
    assert hb.get_adjusted_points() == ((0.0, 0.0), (0.0, 20.0), (20.0, 20.0), (20.0, 0.0))


def test_position():
    hb = hitbox.HitBox(points)
    hb.position = (10.0, 10.0)
    assert hb.position == (10.0, 10.0)
    assert hb.get_adjusted_points() == ((10.0, 10.0), (10.0, 20.0), (20.0, 20.0), (20.0, 10.0))


def test_rotation():
    hb = hitbox.HitBox(points, angle=0.0)
    assert hb.angle == 0.0
    assert hb.position == (0.0, 0.0)
    hb.angle = 90.0
    assert hb.angle == 90.0

    rot_p = hb.get_adjusted_points()
    for i, (a, b) in enumerate(zip(rot_90, rot_p)):
        assert a == pytest.approx(b, abs=1e-6), f"[{i}] {a} != {b}"


def test_angle_constructor():
    hb = hitbox.HitBox(points, angle=90.0)
    rot_p = hb.get_adjusted_points()
    for i, (a, b) in enumerate(zip(rot_90, rot_p)):
        assert a == pytest.approx(b, abs=1e-6), f"[{i}] {a} != {b}"


# --- Multi-region tests ---


def test_multi_region_create():
    body_pts = [(0.0, 0.0), (0.0, 10.0), (10.0, 10.0), (10.0, 0.0)]
    head_pts = [(2.0, 10.0), (2.0, 15.0), (8.0, 15.0), (8.0, 10.0)]
    hb = hitbox.HitBox({"body": body_pts, "head": head_pts})
    assert hb.region_names == ("body", "head")
    assert hb.has_region("body")
    assert hb.has_region("head")
    assert not hb.has_region("default")
    assert hb.regions["body"] == tuple(tuple(p) for p in body_pts)
    assert hb.regions["head"] == tuple(tuple(p) for p in head_pts)


def test_multi_region_adjusted():
    body_pts = [(0.0, 0.0), (0.0, 10.0), (10.0, 10.0), (10.0, 0.0)]
    head_pts = [(2.0, 10.0), (2.0, 15.0), (8.0, 15.0), (8.0, 10.0)]
    hb = hitbox.HitBox({"body": body_pts, "head": head_pts}, position=(5.0, 5.0))
    body_adj = hb.get_adjusted_points("body")
    head_adj = hb.get_adjusted_points("head")
    assert body_adj == ((5.0, 5.0), (5.0, 15.0), (15.0, 15.0), (15.0, 5.0))
    assert head_adj == ((7.0, 15.0), (7.0, 20.0), (13.0, 20.0), (13.0, 15.0))


def test_multi_region_boundaries():
    body_pts = [(0.0, 0.0), (0.0, 10.0), (10.0, 10.0), (10.0, 0.0)]
    head_pts = [(2.0, 10.0), (2.0, 15.0), (8.0, 15.0), (8.0, 10.0)]
    hb = hitbox.HitBox({"body": body_pts, "head": head_pts})
    # Boundaries span all regions
    assert hb.left == 0.0
    assert hb.right == 10.0
    assert hb.bottom == 0.0
    assert hb.top == 15.0


def test_get_all_adjusted_polygons():
    body_pts = [(0.0, 0.0), (0.0, 10.0), (10.0, 10.0), (10.0, 0.0)]
    head_pts = [(2.0, 10.0), (2.0, 15.0), (8.0, 15.0), (8.0, 10.0)]
    hb = hitbox.HitBox({"body": body_pts, "head": head_pts})
    all_polys = hb.get_all_adjusted_polygons()
    assert len(all_polys) == 2


def test_add_remove_region():
    hb = hitbox.HitBox(points)
    assert hb.has_region("default")
    assert len(hb.region_names) == 1

    head_pts = [(2.0, 10.0), (2.0, 15.0), (8.0, 15.0), (8.0, 10.0)]
    hb.add_region("head", head_pts)
    assert hb.has_region("head")
    assert len(hb.region_names) == 2
    assert hb.top == 15.0

    hb.remove_region("head")
    assert not hb.has_region("head")
    assert len(hb.region_names) == 1
    assert hb.top == 10.0


def test_default_region_points():
    hb = hitbox.HitBox(points)
    assert hb.points == points
    assert hb.get_adjusted_points() == hb.get_adjusted_points("default")


def test_single_region_fast_path():
    hb = hitbox.HitBox(points)
    polys = hb.get_all_adjusted_polygons()
    assert len(polys) == 1
    assert polys[0] == points


# --- Serialization tests ---


def test_to_dict_single_region():
    hb = hitbox.HitBox(points)
    d = hb.to_dict()
    assert d["version"] == 1
    assert "default" in d["regions"]
    assert len(d["regions"]) == 1


def test_to_dict_multi_region():
    body_pts = [(0.0, 0.0), (0.0, 10.0), (10.0, 10.0), (10.0, 0.0)]
    head_pts = [(2.0, 10.0), (2.0, 15.0), (8.0, 15.0), (8.0, 10.0)]
    hb = hitbox.HitBox({"body": body_pts, "head": head_pts})
    d = hb.to_dict()
    assert d["version"] == 1
    assert "body" in d["regions"]
    assert "head" in d["regions"]


def test_from_dict():
    d = {
        "version": 1,
        "regions": {
            "default": [[0.0, 0.0], [0.0, 10.0], [10.0, 10.0], [10.0, 0.0]],
        },
    }
    hb = hitbox.HitBox.from_dict(d)
    assert hb.points == ((0.0, 0.0), (0.0, 10.0), (10.0, 10.0), (10.0, 0.0))
    assert hb.get_adjusted_points() == ((0.0, 0.0), (0.0, 10.0), (10.0, 10.0), (10.0, 0.0))


def test_roundtrip_dict():
    body_pts = [(0.0, 0.0), (0.0, 10.0), (10.0, 10.0), (10.0, 0.0)]
    head_pts = [(2.0, 10.0), (2.0, 15.0), (8.0, 15.0), (8.0, 10.0)]
    hb = hitbox.HitBox({"body": body_pts, "head": head_pts})
    d = hb.to_dict()
    hb2 = hitbox.HitBox.from_dict(d, position=(5.0, 5.0))
    assert hb2.has_region("body")
    assert hb2.has_region("head")
    assert hb2.position == (5.0, 5.0)


def test_save_load_json():
    body_pts = [(0.0, 0.0), (0.0, 10.0), (10.0, 10.0), (10.0, 0.0)]
    head_pts = [(2.0, 10.0), (2.0, 15.0), (8.0, 15.0), (8.0, 10.0)]
    hb = hitbox.HitBox({"body": body_pts, "head": head_pts})

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = Path(f.name)

    try:
        hb.save(path)
        hb2 = hitbox.HitBox.load(path, position=(1.0, 2.0))
        assert hb2.has_region("body")
        assert hb2.has_region("head")
        assert hb2.position == (1.0, 2.0)
    finally:
        path.unlink(missing_ok=True)


def test_save_load_gzip():
    hb = hitbox.HitBox(points)

    with tempfile.NamedTemporaryFile(suffix=".gz", delete=False) as f:
        path = Path(f.name)

    try:
        hb.save(path)
        hb2 = hitbox.HitBox.load(path)
        assert hb2.points == ((0.0, 0.0), (0.0, 10.0), (10.0, 10.0), (10.0, 0.0))
    finally:
        path.unlink(missing_ok=True)
