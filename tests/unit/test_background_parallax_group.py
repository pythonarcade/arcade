"""ParallaxGroup offsets each layer by the group offset divided by its depth (#1551)."""

import math

import pytest

from arcade.future.background import Background, ParallaxGroup

TEXTURE = ":resources:images/cybercity_background/far-buildings.png"


def _layer():
    return Background.from_file(TEXTURE)


def test_offset_is_divided_by_depth(window):
    near, far = _layer(), _layer()
    group = ParallaxGroup([near, far], [1.0, 4.0])
    group.offset = (100.0, 40.0)
    assert near.texture.offset == pytest.approx((100.0, 40.0))
    assert far.texture.offset == pytest.approx((25.0, 10.0))


def test_infinite_depth_doesnt_scroll(window):
    sky = _layer()
    group = ParallaxGroup()
    group.add(sky, math.inf)
    group.offset = (100.0, 40.0)
    assert sky.texture.offset == pytest.approx((0.0, 0.0))


def test_depth_zero_is_rejected(window):
    layer = _layer()
    with pytest.raises(ValueError, match="can't be 0"):
        ParallaxGroup([layer], [0.0])

    group = ParallaxGroup()
    with pytest.raises(ValueError, match="can't be 0"):
        group.add(layer, 0)

    group.add(layer, 2.0)
    with pytest.raises(ValueError, match="can't be 0"):
        group.change_depth(layer, 0.0)
    with pytest.raises(ValueError, match="can't be 0"):
        group[0] = 0.0
    # The rejected depths weren't stored, so changing the offset still works
    assert group[0] == (layer, 2.0)
    group.offset = (10.0, 0.0)
    assert layer.texture.offset == pytest.approx((5.0, 0.0))
