import pytest
import arcade


def test_update():
    """Test type sanity checking added in 3.0 due to api change"""
    scene = arcade.Scene()

    # Try old update signature
    with pytest.raises(TypeError):
        scene.update([])
    with pytest.raises(TypeError):
        scene.update([], None)

    scene.update(1, [])
    scene.update(1.0, [])
    scene.update(delta_time=1)
