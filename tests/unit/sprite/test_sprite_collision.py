import random

import pytest

import arcade


def test_sprites_at_point():
    coin_list = arcade.SpriteList()
    sprite = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED)
    # an adjacent sprite with the same level horizontal bottom edge
    sprite2 = arcade.SpriteSolidColor(50, 50, center_x=50, center_y=0, color=arcade.csscolor.RED)

    coin_list.append(sprite)
    coin_list.append(sprite2)

    sprite_list = arcade.get_sprites_at_point((0, 0), coin_list)
    assert len(sprite_list) == 1

    sprite_list = arcade.get_sprites_at_point((50, 0), coin_list)
    assert len(sprite_list) == 1

    sprite_list = arcade.get_sprites_at_point((0, -25), coin_list)
    assert len(sprite_list) == 1

    sprite.position = (130, 130)

    sprite_list = arcade.get_sprites_at_point((0, 0), coin_list)
    assert len(sprite_list) == 0

    sprite_list = arcade.get_sprites_at_point((140, 130), coin_list)
    assert len(sprite_list) == 1

    sprite.angle = 90

    sprite_list = arcade.get_sprites_at_point((0, 0), coin_list)
    assert len(sprite_list) == 0

    sprite_list = arcade.get_sprites_at_point((140, 130), coin_list)
    assert len(sprite_list) == 1


def test_sprite_collides_with_point():
    sprite = arcade.SpriteSolidColor(32, 32, color=arcade.csscolor.RED)
    sprite.width = 2
    sprite.height = 2

    # Affirmative
    point = (0, 0)
    assert sprite.collides_with_point(point) is True
    point = (0, 0.9)
    assert sprite.collides_with_point(point) is True
    point = (0.9, 0)
    assert sprite.collides_with_point(point) is True
    point = (0.9, 0.9)
    assert sprite.collides_with_point(point) is True

    # Negative
    point = (0, 2)
    assert sprite.collides_with_point(point) is False
    point = (2, 0)
    assert sprite.collides_with_point(point) is False
    point = (2, 2)
    assert sprite.collides_with_point(point) is False
    point = (-2, -2)
    assert sprite.collides_with_point(point) is False
    point = (-2, 0)
    assert sprite.collides_with_point(point) is False


def test_sprite_collides_with_sprite():
    sprite_one = arcade.SpriteSolidColor(32, 32, color=arcade.csscolor.RED)
    sprite_one.width = 10
    sprite_one.height = 10

    sprite_two = arcade.SpriteSolidColor(32, 32, color=arcade.csscolor.RED)
    sprite_two.width = 10
    sprite_two.height = 10

    sprite_three = arcade.SpriteSolidColor(32, 32, color=arcade.csscolor.RED)
    sprite_three.width = 1
    sprite_three.height = 1

    # Exact overlap
    assert sprite_one.collides_with_sprite(sprite_two) is True

    # Contains
    assert sprite_one.collides_with_sprite(sprite_three) is True

    # Complete overlap
    assert sprite_three.collides_with_sprite(sprite_one) is True

    # Far away
    sprite_two.center_x = 100
    assert sprite_one.collides_with_sprite(sprite_two) is False

    # border to the right
    sprite_two.center_x = 10
    assert sprite_one.collides_with_sprite(sprite_two) is False

    # Borders, opposite side
    sprite_two.center_x = -10
    assert sprite_one.collides_with_sprite(sprite_two) is False

    # Overlap
    sprite_two.center_x = -9
    assert sprite_one.collides_with_sprite(sprite_two) is True


def test_sprite_collides_with_list():
    coins = arcade.SpriteList()
    for x in range(0, 50, 10):
        coin = arcade.SpriteSolidColor(32, 32, color=arcade.csscolor.RED)
        coin.position = x, 0
        coin.width = 10
        coin.height = 10
        coins.append(coin)

    player = arcade.SpriteSolidColor(32, 32, color=arcade.csscolor.RED)
    player.position = 100, 100
    player.width = 10
    player.height = 10

    # collides with none
    result = player.collides_with_list(coins)
    assert len(result) == 0, "Should return empty list"

    # collides with one
    player.center_x = -5
    player.center_y = 0
    result = player.collides_with_list(coins)
    assert len(result) == 1, "Should collide with one"

    # collides with two
    player.center_x = 5
    result = player.collides_with_list(coins)
    assert len(result) == 2, "Should collide with two"


def test_get_closest_sprite(window):
    a = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED)
    b = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED)
    c = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED)

    a.position = 0, 0
    b.position = 50, 50
    c.position = 100, 0

    sl = arcade.SpriteList()
    sl.extend((c, b))

    # Empty spritelist
    assert arcade.get_closest_sprite(a, arcade.SpriteList()) is None

    # Default closest sprite
    sprite, distance = arcade.get_closest_sprite(a, sl)
    assert sprite == b
    assert distance == pytest.approx(70.710678)


def test_check_for_collision(window):
    a = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED)
    b = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED)
    sp = arcade.SpriteList()

    # Check various incorrect arguments
    with pytest.raises(TypeError):
        arcade.check_for_collision("moo", b)
    with pytest.raises(TypeError):
        arcade.check_for_collision(a, "moo")
    with pytest.raises(TypeError):
        arcade.check_for_collision(a, sp)

    assert arcade.check_for_collision(a, b) is True
    b.position = 100, 0
    assert arcade.check_for_collision(a, b) is False


@pytest.mark.parametrize(
    "scale_a, scale_b",
    [
        ((-1, -1), (1, 1)),
        ((1, 1), (-1, -1)),
        ((-1, -1), (-1, -1)),
        ((-1, 1), (1, -1)),
        ((-2, -2), (0.5, 0.5)),
    ],
)
def test_check_for_collision_negative_scale(window, scale_a, scale_b):
    """Flipping a sprite with a negative scale must not affect collisions."""
    a = arcade.SpriteSolidColor(64, 64, color=arcade.csscolor.RED)
    b = arcade.SpriteSolidColor(64, 64, center_x=20, color=arcade.csscolor.RED)
    a.scale = scale_a
    b.scale = scale_b
    assert arcade.check_for_collision(a, b) is True
    assert arcade.check_for_collision(b, a) is True

    b.position = 500, 0
    assert arcade.check_for_collision(a, b) is False


def test_check_for_collision_with_list(window):
    # TODO: Check that the right collision function is called internally
    a = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED)
    sl = arcade.SpriteList()
    for y in range(40):
        for x in range(40):
            sprite = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED)
            sprite.position = x * 50, y * 50
            sl.append(sprite)

    # There's no good way to perform this test with arcade-accelerate enabled.
    # It causes a very different exception that without the inclusion of pyo3
    # into Arcade would be next to impossible to test for in a sane way.
    if not window.using_accelerate:
        with pytest.raises(TypeError):
            arcade.check_for_collision_with_list("moo", sl)
        with pytest.raises(TypeError):
            arcade.check_for_collision_with_list(a, "moo")

    a.position = 100, 100
    assert len(arcade.check_for_collision_with_list(a, sl)) == 1
    a.position = 75, 75
    assert len(arcade.check_for_collision_with_list(a, sl)) == 4

    # With spatial hash
    sl.enable_spatial_hashing()
    a.position = 100, 100
    assert len(arcade.check_for_collision_with_list(a, sl)) == 1
    a.position = 75, 75
    assert len(arcade.check_for_collision_with_list(a, sl)) == 4


def test_check_for_collision_with_lists(window):
    # TODO: Check that the right collision function is called internally
    a = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED)
    sls = []
    for y in range(10):
        for x in range(10):
            sprite = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED)
            sprite.position = x * 50, y * 50
            sl = arcade.SpriteList()
            sl.append(sprite)
            sls.append(sl)

    # There's no good way to perform this test with arcade-accelerate enabled.
    # It causes a very different exception that without the inclusion of pyo3
    # into Arcade would be next to impossible to test for in a sane way.
    if not window.using_accelerate:
        with pytest.raises(TypeError):
            arcade.check_for_collision_with_lists("moo", sl)

    a.position = 100, 100
    assert len(arcade.check_for_collision_with_lists(a, sls)) == 1
    a.position = 75, 75
    assert len(arcade.check_for_collision_with_lists(a, sls)) == 4

    # With spatial hash
    for sl in sls:
        sl.enable_spatial_hashing()
    a.position = 100, 100
    assert len(arcade.check_for_collision_with_lists(a, sls)) == 1
    a.position = 75, 75
    assert len(arcade.check_for_collision_with_lists(a, sls)) == 4


def test_get_sprites_at_point(window):
    a = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED)
    b = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED)
    sp = arcade.SpriteList()
    sp.extend((a, b))

    with pytest.raises(TypeError):
        arcade.get_sprites_at_point((0, 0), "moo")

    assert set(arcade.get_sprites_at_point((0, 0), sp)) == set([a, b])
    b.position = 100, 0
    assert set(arcade.get_sprites_at_point((0, 0), sp)) == set([a])
    a.position = -100, 0
    assert set(arcade.get_sprites_at_point((0, 0), sp)) == set()

    # With spatial hash
    sp = arcade.SpriteList(use_spatial_hash=True)
    a.position = 0, 0
    b.position = 0, 0
    sp.extend((a, b))
    assert set(arcade.get_sprites_at_point((0, 0), sp)) == set([a, b])
    b.position = 1000, 0
    assert set(arcade.get_sprites_at_point((0, 0), sp)) == set([a])
    a.position = -1000, 0
    assert set(arcade.get_sprites_at_point((0, 0), sp)) == set()


def test_get_sprites_at_exact_point(window):
    a = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED)
    b = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED)
    sp = arcade.SpriteList()
    sp.extend((a, b))

    with pytest.raises(TypeError):
        arcade.get_sprites_at_exact_point((0, 0), "moo")

    assert set(arcade.get_sprites_at_exact_point((0, 0), sp)) == set([a, b])
    b.position = 1, 0
    assert set(arcade.get_sprites_at_exact_point((0, 0), sp)) == set([a])
    a.position = -1, 0
    assert set(arcade.get_sprites_at_exact_point((0, 0), sp)) == set()

    # With spatial hash
    sp = arcade.SpriteList(use_spatial_hash=True)
    sp.extend((a, b))
    a.position = 0, 0
    b.position = 0, 0
    assert set(arcade.get_sprites_at_exact_point((0, 0), sp)) == set([a, b])
    b.position = 1, 0
    assert set(arcade.get_sprites_at_exact_point((0, 0), sp)) == set([a])
    a.position = -1, 0
    assert set(arcade.get_sprites_at_exact_point((0, 0), sp)) == set()


@pytest.mark.parametrize("use_spatial_hash", [True, False])
def test_get_sprites_in_rect(use_spatial_hash):
    a = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED, center_x=50)
    b = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED, center_x=-50)
    c = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED, center_y=50)
    d = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED, center_y=-50)
    sp = arcade.SpriteList(use_spatial_hash=use_spatial_hash)
    sp.extend((a, b, c, d))

    with pytest.raises(TypeError):
        arcade.get_sprites_in_rect(arcade.LRBT(0, 0, 10, 10), "moo")

    assert set(arcade.get_sprites_in_rect(arcade.LRBT(-50, 50, -50, 50), sp)) == {a, b, c, d}
    assert set(arcade.get_sprites_in_rect(arcade.LRBT(100, 200, 100, 200), sp)) == set()
    assert set(arcade.get_sprites_in_rect(arcade.LRBT(-100, 0, -100, 0), sp)) == {b, d}
    assert set(arcade.get_sprites_in_rect(arcade.LRBT(100, 0, 100, 0), sp)) == {a, c}


def test_cpu_collision_with_lazy_list(window):
    """
    Do GPU collision check with lazy list.
    This ensures that check_for_collision_with_list() will trigger
    a spritelist initialization if his is not done yet.
    """
    sprite = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED)
    spritelist = arcade.SpriteList(lazy=True)
    spritelist.append(arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED))
    arcade.check_for_collision_with_list(sprite, spritelist, method=2)


def _reference_check_for_collision(sprite1, sprite2):
    """Collision check using the original separating axis test on every edge."""
    poly_a = sprite1.hit_box.get_adjusted_points()
    poly_b = sprite2.hit_box.get_adjusted_points()
    for polygon in (poly_a, poly_b):
        for i in range(len(polygon)):
            p1, p2 = polygon[i], polygon[(i + 1) % len(polygon)]
            normal = (p2[1] - p1[1], p1[0] - p2[0])
            projected_a = [normal[0] * p[0] + normal[1] * p[1] for p in poly_a]
            projected_b = [normal[0] * p[0] + normal[1] * p[1] for p in poly_b]
            if max(projected_a) <= min(projected_b) or max(projected_b) <= min(projected_a):
                return False
    return True


def test_check_for_collision_matches_reference():
    """Compare against a full polygon test for many random sprite pairs."""
    rng = random.Random(4321)
    textures = [
        arcade.load_texture(":resources:images/tiles/grassMid.png"),  # 4 point box
        arcade.load_texture(":resources:images/items/coinGold.png"),  # 8 point octagon
        arcade.load_texture(":resources:images/space_shooter/laserBlue01.png"),  # long & thin
    ]

    def random_sprite():
        sprite = arcade.Sprite(rng.choice(textures))
        sprite.scale = (rng.choice([-1, 1]) * rng.choice([0.25, 0.5, 1]),
                        rng.choice([-1, 1]) * rng.choice([0.25, 0.5, 1]))  # fmt: skip
        sprite.angle = rng.choice([0, 0, 90, 180, 30, rng.uniform(0, 360)])
        # Integer positions so exact touches happen
        sprite.position = rng.randint(-80, 80), rng.randint(-80, 80)
        return sprite

    results = {True: 0, False: 0}
    for _ in range(5000):
        a, b = random_sprite(), random_sprite()
        expected = _reference_check_for_collision(a, b)
        assert arcade.check_for_collision(a, b) is expected
        assert arcade.check_for_collision(b, a) is expected
        results[expected] += 1
    assert min(results.values()) > 500
