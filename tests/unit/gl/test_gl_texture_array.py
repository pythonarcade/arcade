from array import array

import arcade


def test_create(ctx: arcade.ArcadeContext):
    """Create empty texture array."""
    ta = ctx.texture_array((4, 8, 16), components=1, dtype="f1")
    assert ta.size == (4, 8, 16)
    assert ta.width == 4
    assert ta.height == 8
    assert ta.layers == 16


def test_create_with_data(ctx: arcade.ArcadeContext):
    """Create texture array with initial data."""
    data = array("B")
    data.extend([1] * 16)
    data.extend([2] * 16)
    data.extend([3] * 16)
    data.extend([4] * 16)

    ta = ctx.texture_array((4, 4, 4), components=1, dtype="f1", data=data)
    assert ta.size == (4, 4, 4)
    assert ta.read() == data.tobytes()


def test_create_individual_layers(ctx: arcade.ArcadeContext):
    """Create texture array with individual layers."""
    layer_1 = array("B", [1] * 16)
    layer_2 = array("B", [2] * 16)
    layer_3 = array("B", [3] * 16)
    layer_4 = array("B", [4] * 16)

    layers = array("B")
    layers.extend(layer_1)
    layers.extend(layer_2)
    layers.extend(layer_3)
    layers.extend(layer_4)

    ta = ctx.texture_array((4, 4, 4), components=1, dtype="f1")
    ta.write(layer_1, viewport=(0, 0, 0, 4, 4))
    ta.write(layer_2, viewport=(0, 0, 1, 4, 4))
    ta.write(layer_3, viewport=(0, 0, 2, 4, 4))
    ta.write(layer_4, viewport=(0, 0, 3, 4, 4))

    assert ta.read() == layers.tobytes()

def test_repr(ctx: arcade.ArcadeContext):
    ta = ctx.texture_array((2, 4, 6), components=1, dtype="f1")
    assert repr(ta).startswith("<TextureArray")

