""" Physics engine tests. """

import arcade

OUT_OF_THE_WAY = (250, 250)


def basic_tests(moving_sprite, wall_list, physics_engine):
    """Run basic tests that can be done by both engines."""
    wall_sprite_1 = wall_list[0]
    wall_sprite_2 = wall_list[1]
    wall_sprite_2.position = OUT_OF_THE_WAY

    # --- Collisions between a moving sprite and one wall block

    # Two non-moving sprites side-by-side
    wall_sprite_1.position = (10, 0)
    wall_sprite_1.angle = 0
    moving_sprite.position = (0, 0)
    moving_sprite.angle = 0
    moving_sprite.change_x = 0
    moving_sprite.change_y = 0
    moving_sprite.change_angle = 0
    collisions = physics_engine.update()
    assert moving_sprite.position == (0, 0)
    assert len(collisions) == 0

    # Move up to wall
    wall_sprite_1.position = (11, 0)
    moving_sprite.position = (0, 0)
    moving_sprite.change_x = 1
    moving_sprite.change_y = 0
    collisions = physics_engine.update()
    assert moving_sprite.position == (1, 0)
    assert len(collisions) == 0

    # Move into wall going left to right
    for speed in range(2, 10):
        wall_sprite_1.position = (11, 0)
        moving_sprite.position = (0, 0)
        moving_sprite.change_x = speed
        moving_sprite.change_y = 0
        collisions = physics_engine.update()
        assert moving_sprite.position == (1, 0)
        assert len(collisions) == 1
        assert collisions[0] == wall_sprite_1

    # Move into wall going right to left
    for speed in range(2, 10):
        wall_sprite_1.position = (-11, 0)
        moving_sprite.position = (0, 0)
        moving_sprite.change_x = -speed
        moving_sprite.change_y = 0
        collisions = physics_engine.update()
        assert moving_sprite.position == (-1, 0)
        assert len(collisions) == 1
        assert collisions[0] == wall_sprite_1

    # Move into wall going downwards
    for speed in range(2, 10):
        wall_sprite_1.position = (0, -11)
        moving_sprite.position = (0, 0)
        moving_sprite.change_x = 0
        moving_sprite.change_y = -speed
        collisions = physics_engine.update()
        assert moving_sprite.position == (0, -1)
        assert len(collisions) == 1
        assert collisions[0] == wall_sprite_1

    # Move into wall going up
    for speed in range(2, 10, 1):
        wall_sprite_1.position = (0, 11)
        moving_sprite.position = (0, 0)
        moving_sprite.change_x = 0
        moving_sprite.change_y = speed
        collisions = physics_engine.update()
        assert moving_sprite.position == (0, 1)
        assert len(collisions) == 1
        assert collisions[0] == wall_sprite_1

    # --- Check rotating collision
    # - Rotate, with block to the right
    # Check rotation one degree
    wall_sprite_1.position = (10, 0)
    moving_sprite.position = (0, 0)
    moving_sprite.angle = 0
    moving_sprite.change_x = 0
    moving_sprite.change_y = 0
    moving_sprite.change_angle = 1
    collisions = physics_engine.update()
    assert len(collisions) == 1
    assert collisions[0] == wall_sprite_1
    assert moving_sprite.position == (-1, 0)

    # Check rotation 45 degrees
    wall_sprite_1.position = (10, 0)
    moving_sprite.position = (0, 0)
    moving_sprite.angle = 0
    moving_sprite.change_x = 0
    moving_sprite.change_y = 0
    moving_sprite.change_angle = 45
    collisions = physics_engine.update()
    assert len(collisions) == 1
    assert collisions[0] == wall_sprite_1
    assert moving_sprite.position == (-4, 0)

    # - Rotate, with block to the left
    # Check rotation one degree
    wall_sprite_1.position = (-10, 0)
    moving_sprite.position = (0, 0)
    moving_sprite.angle = 0
    moving_sprite.change_x = 0
    moving_sprite.change_y = 0
    moving_sprite.change_angle = 1
    collisions = physics_engine.update()
    assert len(collisions) == 1
    assert collisions[0] == wall_sprite_1
    assert moving_sprite.position == (1, 0)

    # Check rotation 45 degrees
    wall_sprite_1.position = (-10, 0)
    moving_sprite.position = (0, 0)
    moving_sprite.angle = 0
    moving_sprite.change_x = 0
    moving_sprite.change_y = 0
    moving_sprite.change_angle = 45
    collisions = physics_engine.update()
    assert len(collisions) == 1
    assert collisions[0] == wall_sprite_1
    assert moving_sprite.position == (4, 0)

    # - Rotate, with block above
    # Check rotation one degree
    wall_sprite_1.position = (0, 10)
    moving_sprite.position = (0, 0)
    moving_sprite.angle = 0
    moving_sprite.change_x = 0
    moving_sprite.change_y = 0
    moving_sprite.change_angle = 1
    collisions = physics_engine.update()
    assert len(collisions) == 1
    assert collisions[0] == wall_sprite_1
    assert moving_sprite.position == (0, -1)

    # Check rotation 45 degrees
    wall_sprite_1.position = (0, 10)
    moving_sprite.position = (0, 0)
    moving_sprite.angle = 0
    moving_sprite.change_x = 0
    moving_sprite.change_y = 0
    moving_sprite.change_angle = 45
    collisions = physics_engine.update()
    assert len(collisions) == 1
    assert collisions[0] == wall_sprite_1
    assert moving_sprite.position == (0, -4)

    # - Rotate, between two blocks
    # Check rotation one degree
    wall_sprite_1.position = (10, 0)
    wall_sprite_2.position = (-10, 0)
    moving_sprite.position = (0, 0)
    moving_sprite.angle = 0
    moving_sprite.change_x = 0
    moving_sprite.change_y = 0
    moving_sprite.change_angle = 1
    collisions = physics_engine.update()
    assert len(collisions) == 2
    assert wall_sprite_1 in collisions
    assert wall_sprite_2 in collisions
    assert moving_sprite.position == (0, 0)

    # --- Check pre-existing collision
    wall_sprite_1.position = (9, 0)
    wall_sprite_2.position = OUT_OF_THE_WAY
    moving_sprite.position = (0, 0)
    moving_sprite.angle = 0
    moving_sprite.change_x = 0
    moving_sprite.change_y = 0
    moving_sprite.change_angle = 0
    collisions = physics_engine.update()
    assert moving_sprite.position == (-1, 0)
    assert len(collisions) == 0


def simple_engine_tests(moving_sprite, wall_list, physics_engine):
    wall_sprite_1 = wall_list[0]
    wall_sprite_2 = wall_list[1]
    wall_sprite_2.position = OUT_OF_THE_WAY

    # --- Collide on angle
    wall_sprite_1.position = (15, -5)
    wall_sprite_1.angle = 45
    for speed in range(2, 10):
        moving_sprite.position = (0, 0)
        moving_sprite.angle = 0
        moving_sprite.change_x = speed
        moving_sprite.change_y = 0
        moving_sprite.change_angle = 0
        collisions = physics_engine.update()
        assert moving_sprite.position == (2, 0)
        if speed == 2:
            assert len(collisions) == 0
        else:
            assert len(collisions) == 1

    wall_sprite_1.position = (-15, -5)
    wall_sprite_1.angle = 45
    for speed in range(2, 10):
        moving_sprite.position = (0, 0)
        moving_sprite.angle = 0
        moving_sprite.change_x = -speed
        moving_sprite.change_y = 0
        moving_sprite.change_angle = 0
        collisions = physics_engine.update()
        assert moving_sprite.position == (-2, 0)
        if speed == 2:
            assert len(collisions) == 0
        else:
            assert len(collisions) == 1


def platformer_tests(moving_sprite, wall_list, physics_engine):
    wall_sprite_1 = wall_list[0]
    wall_sprite_2 = wall_list[1]
    wall_sprite_2.position = OUT_OF_THE_WAY

    wall_sprite_1.position = (15, -5)
    wall_sprite_1.angle = 45

    moving_sprite.position = (3, 1)
    moving_sprite.angle = 0
    collisions = arcade.check_for_collision_with_list(moving_sprite, wall_list)
    print(f"\n **** {len(collisions)}")
    print("")
    # --- Collide on angle
    wall_sprite_1.position = (15, -5)
    wall_sprite_1.angle = 45
    for speed in range(2, 7):
        moving_sprite.position = (0, 0)
        moving_sprite.angle = 0
        moving_sprite.change_x = speed
        moving_sprite.change_y = 0
        moving_sprite.change_angle = 0
        collisions = physics_engine.update()
        if speed == 2:
            assert moving_sprite.position == (2, 0)
        elif speed == 3:
            assert moving_sprite.position == (3, 1)
        elif speed == 4:
            assert moving_sprite.position == (4, 2)
        elif speed == 5:
            assert moving_sprite.position == (5, 3)
        elif speed == 6:
            assert moving_sprite.position == (6, 4)

    wall_sprite_1.position = (-15, -5)
    wall_sprite_1.angle = 45
    for speed in range(2, 7):
        moving_sprite.position = (0, 0)
        moving_sprite.angle = 0
        moving_sprite.change_x = -speed
        moving_sprite.change_y = 0
        moving_sprite.change_angle = 0
        collisions = physics_engine.update()
        if speed == 2:
            assert moving_sprite.position == (-2, 0)
        elif speed == 3:
            assert moving_sprite.position == (-3, 1)
        elif speed == 4:
            assert moving_sprite.position == (-4, 2)
        elif speed == 5:
            assert moving_sprite.position == (-5, 3)
        elif speed == 6:
            assert moving_sprite.position == (-6, 4)

    # Move up to wall
    wall_sprite_1.position = OUT_OF_THE_WAY
    physics_engine.gravity_constant = 1
    moving_sprite.position = (0, 0)
    moving_sprite.change_x = 1
    moving_sprite.change_y = 0
    collisions = physics_engine.update()
    assert moving_sprite.position == (1, -1)
    collisions = physics_engine.update()
    assert moving_sprite.position == (2, -3)
    collisions = physics_engine.update()
    assert moving_sprite.position == (3, -6)


def test_main(window: arcade.Window):
    character_list = arcade.SpriteList()
    wall_list = arcade.SpriteList()
    moving_sprite = arcade.SpriteSolidColor(width=10, height=10, color=arcade.color.RED)
    character_list.append(moving_sprite)

    wall_sprite = arcade.SpriteSolidColor(width=10, height=10, color=arcade.color.BLUE)
    wall_list.append(wall_sprite)

    wall_sprite = arcade.SpriteSolidColor(10, 10, color=arcade.color.BLUE)
    wall_sprite.position = OUT_OF_THE_WAY
    wall_list.append(wall_sprite)

    physics_engine = arcade.PhysicsEngineSimple(moving_sprite, wall_list)
    basic_tests(moving_sprite, wall_list, physics_engine)
    simple_engine_tests(moving_sprite, wall_list, physics_engine)

    physics_engine = arcade.PhysicsEnginePlatformer(
        moving_sprite, wall_list, gravity_constant=0.0
    )
    basic_tests(moving_sprite, wall_list, physics_engine)
    platformer_tests(moving_sprite, wall_list, physics_engine)
