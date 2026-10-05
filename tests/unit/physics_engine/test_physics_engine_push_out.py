"""
Tests for how the simple and platformer physics engines move sprites out of walls.
"""

import math
import random

import pytest

import arcade
from arcade.sprite_list.collision import _get_separation_distance

R = ":resources:images/"


def make_walls(*walls):
    wall_list = arcade.SpriteList()
    wall_list.extend(walls)
    return wall_list


def box(width, height, x=0.0, y=0.0, angle=0.0):
    sprite = arcade.SpriteSolidColor(width, height, center_x=x, center_y=y)
    sprite.angle = angle
    return sprite


@pytest.mark.parametrize("fall_speed", [0.3, 1, 5, 7.7, 18, 31])
def test_land_exactly_on_floor(window, fall_speed):
    """Landing leaves the sprite exactly on the floor, without a gap"""
    floor = box(200, 20, y=-10)  # Top at y=0
    player = box(10, 10, y=5 + fall_speed - 0.1)  # Overlaps the floor after falling
    engine = arcade.PhysicsEnginePlatformer(player, walls=make_walls(floor), gravity_constant=0)
    player.change_y = -fall_speed

    hits = engine.update()
    assert hits == [floor]
    assert player.bottom == pytest.approx(0, abs=1e-9)
    assert not arcade.check_for_collision(player, floor)
    assert engine.can_jump()


@pytest.mark.parametrize("slope", [5, 12, 30, -20])
def test_land_on_ramp(window, slope):
    """Landing on a rotated wall rests the sprite on its surface"""
    ramp = box(200, 20, angle=slope)
    walls = make_walls(ramp)
    player = box(10, 10, x=30, y=60)
    engine = arcade.PhysicsEnginePlatformer(player, walls=walls, gravity_constant=1)
    for _ in range(60):
        engine.update()

    assert not arcade.check_for_collision(player, ramp)
    # Resting on it: y is rounded to 2 decimal places, so within 0.01
    player.center_y -= 0.011
    assert arcade.check_for_collision(player, ramp)


@pytest.mark.parametrize("speed", [0.4, 1, 6, 13.3])
def test_ceiling_bump_exact(window, speed):
    """Jumping into a ceiling stops the sprite right below it"""
    ceiling = box(200, 20, y=60)  # Bottom at y=50
    player = box(10, 10, y=45 - speed + 0.1)
    engine = arcade.PhysicsEnginePlatformer(player, walls=make_walls(ceiling), gravity_constant=0)
    player.change_y = speed

    assert engine.update() == [ceiling]
    assert not arcade.check_for_collision(player, ceiling)
    assert player.top == pytest.approx(50, abs=0.01)
    assert player.change_y == 0


@pytest.mark.parametrize("engine_type", ["simple", "platformer"])
@pytest.mark.parametrize("change_x", [-3, 2, 5])
def test_rotate_while_moving_sideways(window, engine_type, change_x):
    """Rotating against a wall while moving sideways doesn't end in the wall"""
    wall = box(20, 200, x=20)  # Left edge at x=10
    walls = make_walls(wall)
    player = box(10, 20, x=4.9)
    if engine_type == "simple":
        engine = arcade.PhysicsEngineSimple(player, walls)
    else:
        engine = arcade.PhysicsEnginePlatformer(player, walls=walls, gravity_constant=0)

    player.change_x = change_x
    player.change_angle = 3
    for _ in range(40):
        engine.update()
        assert not arcade.check_for_collision(player, wall)


@pytest.mark.parametrize("engine_type", ["simple", "platformer"])
def test_start_overlapping_wedged(window, engine_type):
    """Starting wedged between two walls still frees the sprite (using the fallback search)"""
    left = box(20, 20, x=-12)
    right = box(20, 20, x=12)
    walls = make_walls(left, right)
    player = box(10, 10)  # Overlaps both walls by 3 pixels
    if engine_type == "simple":
        engine = arcade.PhysicsEngineSimple(player, walls)
    else:
        engine = arcade.PhysicsEnginePlatformer(player, walls=walls, gravity_constant=0)

    engine.update()
    assert not arcade.check_for_collision_with_list(player, walls)


def test_start_overlapping_concave_wall(window):
    """A wall with a concave detailed hit box still frees the sprite"""
    texture = arcade.load_texture(
        R + "space_shooter/meteorGrey_big1.png", hit_box_algorithm=arcade.hitbox.algo_detailed
    )
    meteor = arcade.Sprite(texture)
    walls = make_walls(meteor)
    for x, y in ((0, 0), (30, 10), (-40, -20), (10, 35)):
        player = box(10, 10, x=x, y=y)
        engine = arcade.PhysicsEngineSimple(player, walls)
        engine.update()
        assert not arcade.check_for_collision(player, meteor)


@pytest.mark.parametrize("engine_type", ["simple", "platformer"])
def test_start_overlapping_smallest_move(window, engine_type):
    """A sprite starting inside a wall is moved out the shortest way"""
    wall = box(40, 40, angle=30)
    walls = make_walls(wall)
    player = box(10, 10, x=18, y=3)
    expected = arcade.get_collision_info(player, wall)
    start = player.position
    if engine_type == "simple":
        engine = arcade.PhysicsEngineSimple(player, walls)
    else:
        engine = arcade.PhysicsEnginePlatformer(player, walls=walls, gravity_constant=0)

    engine.update()
    assert not arcade.check_for_collision(player, wall)
    moved = math.dist(start, player.position)
    # Exactly the smallest move, apart from rounding y to 2 decimal places
    assert moved == pytest.approx(expected.depth, abs=0.011)


def test_separation_distance(window):
    """_get_separation_distance is the exact distance to move along a direction"""
    rng = random.Random(10)
    textures = [
        arcade.load_texture(R + "tiles/grassMid.png"),
        arcade.load_texture(R + "items/coinGold.png"),
        arcade.load_texture(R + "space_shooter/laserBlue01.png"),
    ]

    def random_sprite():
        sprite = arcade.Sprite(rng.choice(textures))
        sprite.scale = (rng.choice([-1, 1]) * rng.choice([0.25, 0.5, 1]),
                        rng.choice([-1, 1]) * rng.choice([0.25, 0.5, 1]))  # fmt: skip
        sprite.angle = rng.choice([0, 90, 30, rng.uniform(0, 360)])
        sprite.position = rng.randint(-80, 80) / 2, rng.randint(-80, 80) / 2
        return sprite

    checked = 0
    for _ in range(3000):
        a, b = random_sprite(), random_sprite()
        angle = rng.choice([90, -90, 0, 180, rng.uniform(0, 360)])
        dx = round(math.cos(math.radians(angle)), 12)
        dy = round(math.sin(math.radians(angle)), 12)
        distance = _get_separation_distance(a, b, dx, dy)
        colliding = arcade.check_for_collision(a, b)
        assert (distance > 0) is colliding
        if not colliding:
            continue
        checked += 1
        start = a.position
        a.position = start[0] + dx * (distance + 1e-6), start[1] + dy * (distance + 1e-6)
        assert not arcade.check_for_collision(a, b)
        if distance > 1e-5:
            a.position = start[0] + dx * (distance - 1e-6), start[1] + dy * (distance - 1e-6)
            assert arcade.check_for_collision(a, b)
        a.position = start
    assert checked > 300
