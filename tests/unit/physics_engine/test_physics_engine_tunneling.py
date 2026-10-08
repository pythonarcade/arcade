"""
Fast sprites in the physics engines stop at thin walls instead of passing
through them. A sprite that moved farther than its own size plus the wall's
thickness in one frame used to jump right over the wall.
"""

import pytest

import arcade

SIZE = 32


def _wall(center_x, center_y, width, height):
    walls = arcade.SpriteList()
    walls.append(arcade.SpriteSolidColor(width, height, center_x=center_x, center_y=center_y))
    return walls


@pytest.mark.parametrize("speed", [20, 50, 100, 400])
@pytest.mark.parametrize("thickness", [1, 10])
@pytest.mark.parametrize("direction", [1, -1])
def test_simple_engine_x(speed, thickness, direction):
    player = arcade.SpriteSolidColor(SIZE, SIZE, center_x=0, center_y=0)
    walls = _wall(100 * direction, 0, thickness, 200)
    wall = walls[0]
    engine = arcade.PhysicsEngineSimple(player, walls)
    player.change_x = speed * direction

    hit = False
    for _ in range(30):
        hit = hit or wall in engine.update()
    assert hit
    if direction > 0:
        assert player.right == pytest.approx(wall.left, abs=1)
    else:
        assert player.left == pytest.approx(wall.right, abs=1)


@pytest.mark.parametrize("speed", [20, 50, 100, 400])
@pytest.mark.parametrize("thickness", [1, 10])
@pytest.mark.parametrize("direction", [1, -1])
def test_simple_engine_y(speed, thickness, direction):
    player = arcade.SpriteSolidColor(SIZE, SIZE, center_x=0, center_y=0)
    walls = _wall(0, 100 * direction, 200, thickness)
    wall = walls[0]
    engine = arcade.PhysicsEngineSimple(player, walls)
    player.change_y = speed * direction

    hit = False
    for _ in range(30):
        hit = hit or wall in engine.update()
    assert hit
    if direction > 0:
        assert player.top == pytest.approx(wall.bottom, abs=1)
    else:
        assert player.bottom == pytest.approx(wall.top, abs=1)


@pytest.mark.parametrize("fall_speed", [10, 30, 45, 100, 500])
def test_platformer_lands_on_thin_platform(fall_speed):
    """Falling fast enough used to drop through a thin platform, depending on the frame"""
    player = arcade.SpriteSolidColor(SIZE, SIZE, center_x=0, center_y=600)
    platforms = _wall(0, 0, 400, 4)
    engine = arcade.PhysicsEnginePlatformer(player, walls=platforms, gravity_constant=1)
    player.change_y = -fall_speed
    for _ in range(80):
        engine.update()
    assert player.bottom == pytest.approx(platforms[0].top, abs=1)
    assert engine.can_jump()


@pytest.mark.parametrize("speed", [50, 100, 400])
def test_platformer_runs_into_thin_wall(speed):
    player = arcade.SpriteSolidColor(SIZE, SIZE, center_x=0, center_y=SIZE / 2 + 2)
    walls = arcade.SpriteList()
    walls.append(arcade.SpriteSolidColor(1000, 4, center_x=0, center_y=0))
    wall = arcade.SpriteSolidColor(4, 300, center_x=150, center_y=150)
    walls.append(wall)
    engine = arcade.PhysicsEnginePlatformer(player, walls=walls, gravity_constant=1)
    player.change_x = speed
    for _ in range(30):
        engine.update()
        player.change_x = speed
    assert player.right == pytest.approx(wall.left, abs=1)


def test_fast_sprite_stops_at_first_of_several_walls():
    player = arcade.SpriteSolidColor(SIZE, SIZE, center_x=0, center_y=0)
    walls = arcade.SpriteList()
    for x in (100, 140, 180):
        walls.append(arcade.SpriteSolidColor(4, 200, center_x=x, center_y=0))
    engine = arcade.PhysicsEngineSimple(player, walls)
    player.change_x = 500
    engine.update()
    assert player.right == pytest.approx(walls[0].left, abs=1)
