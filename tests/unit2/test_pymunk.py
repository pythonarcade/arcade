import arcade


def test_pymunk():
    physics_engine = arcade.PymunkPhysicsEngine(damping=1.0,
                                                gravity=(0, -100))

    my_sprite = arcade.SpriteSolidColor(50, 50, arcade.color.WHITE)

    assert my_sprite.center_x == 0
    assert my_sprite.center_y == 0

    physics_engine.add_sprite(my_sprite)

    physics_engine.step(1.0)
    assert(my_sprite.center_y == 0)

    physics_engine.step(1.0)
    assert(my_sprite.center_y == -100.0)

    physics_engine.step(1.0)
    assert(my_sprite.center_y == -300.0)
