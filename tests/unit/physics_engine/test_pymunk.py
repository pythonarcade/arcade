import pytest
import arcade


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
