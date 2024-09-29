import pymunk.autogeometry
import pytest
from PIL import Image

import arcade
from arcade.hitbox import PymunkHitBoxAlgorithm


def test_pymunk():
    physics_engine = arcade.PymunkPhysicsEngine(damping=1.0,
                                                gravity=(0, -100))

    my_sprite = arcade.SpriteSolidColor(50, 50, color=arcade.color.WHITE)

    assert my_sprite.center_x == 0
    assert my_sprite.center_y == 0

    physics_engine.add_sprite(my_sprite)

    physics_engine.step(1.0)
    assert(my_sprite.center_y == 0)

    physics_engine.step(1.0)
    assert(my_sprite.center_y == -100.0)

    physics_engine.step(1.0)
    assert(my_sprite.center_y == -300.0)


# Temp fix for https://github.com/pythonarcade/arcade/issues/2074
def test_pymunk_engine_nocopy():
    import copy
    physics_engine = arcade.PymunkPhysicsEngine(
        damping=1.0, gravity=(0, -100))

    with pytest.raises(NotImplementedError):
        _ = copy.copy(physics_engine)
    with pytest.raises(NotImplementedError):
        _ = copy.deepcopy(physics_engine)


@pytest.mark.parametrize("moment_of_inertia_arg_name",
                         (
                             "moment_of_inertia",
                         ))
def test_pymunk_add_sprite_moment_backwards_compatibility(moment_of_inertia_arg_name):
    """
    Ensure that all supported kwarg aliases for moment of inertia work
    """
    physics_engine = arcade.PymunkPhysicsEngine(damping=1.0, gravity=(0,0))

    sprite = arcade.SpriteSolidColor(32, 32, color=arcade.color.RED)

    # Choose a non-default value that we can check was set
    kwargs = {moment_of_inertia_arg_name: arcade.PymunkPhysicsEngine.MOMENT_INF}

    physics_engine.add_sprite(sprite, **kwargs)

    set_moment = physics_engine.get_physics_object(sprite).body.moment

    assert set_moment == arcade.PymunkPhysicsEngine.MOMENT_INF


def test_pymunk_hitbox_algorithm_trace_image_only_takes_rgba():
    """Test whether non-RGBA modes raise a ValueError.

    We expect the hitbox algo to take RGBA image because the alpha
    channel is how we determine whether a pixel is empty. See the
    pillow doc for more on the modes offered:
    https://pillow.readthedocs.io/en/stable/handbook/concepts.html#modes
    """

    algo = PymunkHitBoxAlgorithm()
    def mode(m: str) -> Image.Image:
        return Image.new(
            m, # type: ignore
            (10, 10), 0)

    with pytest.raises(ValueError):
        algo.trace_image(mode("1"))

    with pytest.raises(ValueError):
        algo.trace_image(mode("L"))

    with pytest.raises(ValueError):
        algo.trace_image(mode("P"))

    with pytest.raises(ValueError):
        algo.trace_image(mode("RGB"))

    with pytest.raises(ValueError):
        algo.trace_image(mode("HSV"))

    assert isinstance(
        algo.trace_image(mode("RGBA")), pymunk.autogeometry.PolylineSet)

