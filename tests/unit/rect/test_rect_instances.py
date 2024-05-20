import pytest
from pyglet.math import Vec2
from arcade.types.rect import Rect, LBWH, LRBT, XYRR, XYWH


A_RECT = Rect(10, 20, 10, 20, 10, 10, 15, 15)


def test_attributes():
    assert A_RECT.left == 10.0
    assert A_RECT.bottom == 10.0
    assert A_RECT.width == 10.0
    assert A_RECT.height == 10.0
    assert A_RECT.top == 20.0
    assert A_RECT.right == 20.0
    assert A_RECT.x == 15.0
    assert A_RECT.y == 15.0


def test_equivalency():
    assert LBWH(10, 10, 10, 10) == LRBT(10, 20, 10, 20) == XYWH(15, 15, 10, 10) == XYRR(15, 15, 5, 5) == A_RECT


def test_corners():
    assert A_RECT.bottom_left == Vec2(10, 10)
    assert A_RECT.bottom_right == Vec2(20, 10)
    assert A_RECT.top_left == Vec2(10, 20)
    assert A_RECT.top_right == Vec2(20, 20)


def test_centers():
    assert A_RECT.center == Vec2(15, 15)
    assert A_RECT.bottom_center == Vec2(15, 10)
    assert A_RECT.top_center == Vec2(15, 20)
    assert A_RECT.left_center == Vec2(10, 15)
    assert A_RECT.right_center == Vec2(20, 15)


def test_rect_move():
    r = A_RECT.move(5, 5)
    assert r.x == 20
    assert r.y == 20


def test_point_in_rect():
    p = Vec2(15, 15)
    assert A_RECT.point_in_rect(p)


def test_point_not_in_rect():
    p = Vec2(25, 25)
    assert not A_RECT.point_in_rect(p)


def test_union():
    a_rect = LBWH(10, 10, 10, 10)
    another_rect = LBWH(15, 10, 10, 10)
    assert a_rect.union(another_rect) == LBWH(10, 10, 15, 10)
    assert a_rect | another_rect == LBWH(10, 10, 15, 10)


def test_overlap():
    a_rect = LBWH(10, 10, 10, 10)
    another_rect = LBWH(15, 10, 10, 10)
    assert a_rect.intersect(another_rect) == LBWH(15, 10, 5, 10)
    assert a_rect & another_rect == LBWH(15, 10, 5, 10)


def test_size():
    assert A_RECT.size == Vec2(10, 10)


def test_at_position():
    r = A_RECT.at_position(Vec2(20, 20))
    assert r.left == 15
    assert r.right == 25
    assert r.bottom == 15
    assert r.top == 25


def test_views():
    assert A_RECT.lrbt == (10, 20, 10, 20)
    assert A_RECT.lbwh == (10, 10, 10, 10)
    assert A_RECT.xyrr == (15, 15,  5,  5)
    assert A_RECT.xywh == (15, 15, 10, 10)
    assert A_RECT.viewport == (10, 20, 10, 20)


class SubclassedRect(Rect):
    ...

@pytest.fixture(params=(Rect, SubclassedRect))
def rect_type(request):
    return request.param


@pytest.fixture
def rect_instance(rect_type):
    return rect_type(*(0 for _ in Rect._fields))


def test_repr_inheritance_safety(rect_type, rect_instance):
     assert repr(rect_instance).startswith(f"{rect_type.__name__}")


def test_str_inheritance_safety(rect_type, rect_instance):
     assert str(rect_instance).startswith(f"<{rect_type.__name__}")
