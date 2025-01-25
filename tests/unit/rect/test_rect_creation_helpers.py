from __future__ import annotations

import pytest

from arcade.types.rect import LBWH, LRBT, XYWH, XYRR, Rect


def test_make_LBWH():
    r = LBWH(10, 10, 10, 10)
    assert r.left == 10.0
    assert r.bottom == 10.0
    assert r.width == 10.0
    assert r.height == 10.0
    assert r.top == 20.0
    assert r.right == 20.0
    assert r.x == 15.0
    assert r.y == 15.0


def test_make_LRBT():
    r = LRBT(10, 20, 10, 20)
    assert r.left == 10.0
    assert r.bottom == 10.0
    assert r.width == 10.0
    assert r.height == 10.0
    assert r.top == 20.0
    assert r.right == 20.0
    assert r.x == 15.0
    assert r.y == 15.0


def test_make_XYWH():
    r = XYWH(15, 15, 10, 10)
    assert r.left == 10.0
    assert r.bottom == 10.0
    assert r.width == 10.0
    assert r.height == 10.0
    assert r.top == 20.0
    assert r.right == 20.0
    assert r.x == 15.0
    assert r.y == 15.0


def test_make_XYRR():
    r = XYRR(15, 15, 10, 5)
    assert r.left == 5.0
    assert r.bottom == 10.0
    assert r.width == 20.0
    assert r.height == 10.0
    assert r.top == 20.0
    assert r.right == 25.0
    assert r.x == 15.0
    assert r.y == 15.0


def test_kwargtangle_missing_args():
    # Zero args raises ValueError
    with pytest.raises(ValueError):
        _ = Rect.from_kwargs()

    # LRBT
    with pytest.raises(ValueError):
        _ = Rect.from_kwargs(left=0, right=0, bottom=0)

    with pytest.raises(ValueError):
        _ = Rect.from_kwargs(left=0, right=0, top=0)

    with pytest.raises(ValueError):
        _ = Rect.from_kwargs(left=0, top=0, bottom=0)

    with pytest.raises(ValueError):
        _ = Rect.from_kwargs(right=0, top=0, bottom=0)

    # LBWH
    with pytest.raises(ValueError):
        _ = Rect.from_kwargs(left=0, bottom=0, width=0)

    with pytest.raises(ValueError):
        _ = Rect.from_kwargs(left=0, bottom=0, height=0)

    with pytest.raises(ValueError):
        _ = Rect.from_kwargs(left=0, width=0, height=0)

    with pytest.raises(ValueError):
        _ = Rect.from_kwargs(bottom=0, width=0, height=0)

    # XYWH
    with pytest.raises(ValueError):
        _ = Rect.from_kwargs(x=0, y=0, width=0)

    with pytest.raises(ValueError):
        _ = Rect.from_kwargs(x=0, y=0, height=0)

    with pytest.raises(ValueError):
        _ = Rect.from_kwargs(y=0, width=0, height=0)

    with pytest.raises(ValueError):
        _ = Rect.from_kwargs(x=0, width=0, height=0)


def test_kwargtangle_none_args():

    # LRBT
    with pytest.raises(ValueError):
        _ = Rect.from_kwargs(left=0, right=0, bottom=0, top=None)

    with pytest.raises(ValueError):
        _ = Rect.from_kwargs(left=0, right=0, bottom=None, top=0)

    with pytest.raises(ValueError):
        _ = Rect.from_kwargs(left=0, right=None, top=0, bottom=0)

    with pytest.raises(ValueError):
        _ = Rect.from_kwargs(left = None, right=0, top=0, bottom=0)

    # LBWH
    with pytest.raises(ValueError):
        _ = Rect.from_kwargs(left=0, bottom=0, width=0, height=None)

    with pytest.raises(ValueError):
        _ = Rect.from_kwargs(left=0, bottom=0, width=None, height=0)

    with pytest.raises(ValueError):
        _ = Rect.from_kwargs(left=0, bottom=None, width=0, height=0)

    with pytest.raises(ValueError):
        _ = Rect.from_kwargs(left=None, bottom=0, width=0, height=0)

    # XYWH
    with pytest.raises(ValueError):
        _ = Rect.from_kwargs(x=0, y=0, width=0, height=None)

    with pytest.raises(ValueError):
        _ = Rect.from_kwargs(x=0, y=0, width=None, height=0)

    with pytest.raises(ValueError):
        _ = Rect.from_kwargs(x=None, y=0, width=0, height=0)

    with pytest.raises(ValueError):
        _ = Rect.from_kwargs(x=0, y=None, width=0, height=0)
