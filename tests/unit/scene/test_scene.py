import pytest
import arcade


def test_update():
    """Test type sanity checking added in 3.0 due to api change"""
    scene = arcade.Scene()
    with pytest.raises(TypeError):
        scene.update(0)

    scene.update([])
    scene.update([], delta_time=1)
    scene.update(delta_time=1)
